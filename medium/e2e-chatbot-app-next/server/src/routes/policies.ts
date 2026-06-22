import {
  Router,
  type Request,
  type Response,
  type Router as RouterType,
} from 'express';
import { getDatabricksToken, getCachedCliHost } from '@chat-template/auth';
import { getHostUrl } from '@chat-template/utils';
import {
  savePolicyReview,
  savePolicyUpload,
  listPolicyUploads,
  updatePolicyUploadContent,
} from '@chat-template/db';

export const policiesRouter: RouterType = Router();

// Unity Catalog table holding one row per policy (see the policy setup notebook).
const POLICIES_TABLE = process.env.POLICIES_TABLE || 'dev.policies.policy_docs';
// SQL warehouse used to run the compliance queries.
const WAREHOUSE_ID =
  process.env.DATABRICKS_SQL_WAREHOUSE_ID ||
  process.env.DATABRICKS_WAREHOUSE_ID ||
  '';
// A policy is "due soon" if its review date falls within this many days.
const DUE_SOON_DAYS = 90;
// Approving a policy resets its review clock by this many months (annual cycle).
const REVIEW_CYCLE_MONTHS = 12;

type Row = Record<string, string | null>;

interface PolicyRow {
  policyId: string;
  docName: string;
  category: string;
  title: string;
  owner: string;
  version: string;
  effectiveDate: string;
  reviewDate: string;
  daysOverdue: number; // >0 means past its review date
  ageDays: number; // days since effective date
  status: 'Overdue' | 'Due soon' | 'Current';
  reviewStatus: string | null; // 'Approved' | 'Changes requested' | null
  reviewComment: string | null;
  reviewedBy: string | null;
  reviewedAt: string | null;
}

/** Resolve the workspace base URL, preferring an explicit host then the CLI cache. */
function resolveHost(): string {
  const raw = process.env.DATABRICKS_HOST || getCachedCliHost() || undefined;
  return getHostUrl(raw);
}

/**
 * Execute a SQL statement on the configured warehouse and return rows as
 * objects keyed by column name. Polls briefly if the statement is still running.
 */
async function runSql(statement: string): Promise<Row[]> {
  if (!WAREHOUSE_ID) {
    throw new Error(
      'No SQL warehouse configured. Set DATABRICKS_SQL_WAREHOUSE_ID in your environment ' +
        '(or as a Databricks App resource).',
    );
  }

  const token = await getDatabricksToken();
  const host = resolveHost();
  const baseHeaders = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  const post = await fetch(`${host}/api/2.0/sql/statements/`, {
    method: 'POST',
    headers: baseHeaders,
    body: JSON.stringify({
      statement,
      warehouse_id: WAREHOUSE_ID,
      format: 'JSON_ARRAY',
      disposition: 'INLINE',
      wait_timeout: '30s',
    }),
  });

  if (!post.ok) {
    throw new Error(
      `SQL statement request failed (${post.status}): ${await post.text()}`,
    );
  }

  let payload = (await post.json()) as {
    statement_id?: string;
    status?: { state?: string; error?: { message?: string } };
    manifest?: { schema?: { columns?: { name: string }[] } };
    result?: { data_array?: (string | null)[][] };
  };

  // Poll while the statement is still executing.
  const terminal = new Set(['SUCCEEDED', 'FAILED', 'CANCELED', 'CLOSED']);
  let attempts = 0;
  while (
    payload.statement_id &&
    !terminal.has(payload.status?.state ?? '') &&
    attempts < 15
  ) {
    await new Promise((r) => setTimeout(r, 1500));
    const poll = await fetch(
      `${host}/api/2.0/sql/statements/${payload.statement_id}`,
      { headers: baseHeaders },
    );
    payload = (await poll.json()) as typeof payload;
    attempts += 1;
  }

  const state = payload.status?.state;
  if (state !== 'SUCCEEDED') {
    throw new Error(
      `SQL statement did not succeed (state=${state ?? 'unknown'}): ` +
        `${payload.status?.error?.message ?? 'no detail'}`,
    );
  }

  const columns = (payload.manifest?.schema?.columns ?? []).map((c) => c.name);
  const dataArray = payload.result?.data_array ?? [];
  return dataArray.map((arr) => {
    const row: Row = {};
    columns.forEach((name, i) => {
      row[name] = arr[i] ?? null;
    });
    return row;
  });
}

function toInt(v: string | null): number {
  const n = Number.parseInt(v ?? '', 10);
  return Number.isFinite(n) ? n : 0;
}

/**
 * GET /api/policies/compliance
 * Returns policy staleness / review-compliance metrics computed from the
 * Unity Catalog policy table: KPI summary, per-category breakdown, and a
 * per-policy list ordered by how overdue each review is.
 */
policiesRouter.get(
  '/compliance',
  async (_req: Request, res: Response): Promise<void> => {
    try {
      const rows = await runSql(`
        SELECT
          policy_id,
          doc_name,
          category,
          title,
          owner,
          version,
          CAST(effective_date AS STRING) AS effective_date,
          CAST(review_date AS STRING)    AS review_date,
          DATEDIFF(current_date(), review_date)    AS days_overdue,
          DATEDIFF(current_date(), effective_date) AS age_days,
          CASE
            WHEN review_date < current_date() THEN 'Overdue'
            WHEN review_date <= DATE_ADD(current_date(), ${DUE_SOON_DAYS}) THEN 'Due soon'
            ELSE 'Current'
          END AS status,
          review_status,
          review_comment,
          reviewed_by,
          CAST(reviewed_at AS STRING) AS reviewed_at
        FROM ${POLICIES_TABLE}
        ORDER BY days_overdue DESC, review_date ASC
      `);

      const policies: PolicyRow[] = rows.map((r) => ({
        policyId: r.policy_id ?? '',
        docName: r.doc_name ?? '',
        category: r.category ?? 'Uncategorized',
        title: r.title ?? '',
        owner: r.owner ?? '',
        version: r.version ?? '',
        effectiveDate: r.effective_date ?? '',
        reviewDate: r.review_date ?? '',
        daysOverdue: toInt(r.days_overdue),
        ageDays: toInt(r.age_days),
        status: (r.status as PolicyRow['status']) ?? 'Current',
        reviewStatus: r.review_status,
        reviewComment: r.review_comment,
        reviewedBy: r.reviewed_by,
        reviewedAt: r.reviewed_at,
      }));

      const total = policies.length;
      const overdue = policies.filter((p) => p.status === 'Overdue').length;
      const dueSoon = policies.filter((p) => p.status === 'Due soon').length;
      const current = policies.filter((p) => p.status === 'Current').length;
      const staleOverYear = policies.filter((p) => p.ageDays > 365).length;
      const avgAgeDays = total
        ? Math.round(policies.reduce((s, p) => s + p.ageDays, 0) / total)
        : 0;
      const effectiveDates = policies
        .map((p) => p.effectiveDate)
        .filter(Boolean)
        .sort();

      const byCategoryMap = new Map<
        string,
        {
          category: string;
          total: number;
          overdue: number;
          dueSoon: number;
          current: number;
        }
      >();
      for (const p of policies) {
        const entry = byCategoryMap.get(p.category) ?? {
          category: p.category,
          total: 0,
          overdue: 0,
          dueSoon: 0,
          current: 0,
        };
        entry.total += 1;
        if (p.status === 'Overdue') entry.overdue += 1;
        else if (p.status === 'Due soon') entry.dueSoon += 1;
        else entry.current += 1;
        byCategoryMap.set(p.category, entry);
      }
      const byCategory = [...byCategoryMap.values()].sort(
        (a, b) => b.overdue - a.overdue || b.total - a.total,
      );

      res.json({
        generatedAt: new Date().toISOString(),
        table: POLICIES_TABLE,
        summary: {
          total,
          overdue,
          dueSoon,
          current,
          staleOverYear,
          avgAgeDays,
          pctOverdue: total ? Math.round((overdue / total) * 100) : 0,
          oldestEffective: effectiveDates[0] ?? null,
          newestEffective: effectiveDates[effectiveDates.length - 1] ?? null,
        },
        byCategory,
        policies,
      });
    } catch (error) {
      console.error('[/api/policies/compliance] Error:', error);
      res.status(500).json({
        error: 'policies_query_failed',
        message: error instanceof Error ? error.message : String(error),
      });
    }
  },
);

/**
 * GET /api/policies/content/:policyId
 * Returns the full Markdown content (and key metadata) for a single policy,
 * fetched on demand when a reviewer opens a policy.
 */
policiesRouter.get(
  '/content/:policyId',
  async (req: Request, res: Response): Promise<void> => {
    try {
      const policyId = String(req.params.policyId ?? '');
      const rows = await runSql(`
        SELECT policy_id, title, category, owner, version, content
        FROM ${POLICIES_TABLE}
        WHERE policy_id = ${sqlString(policyId)}
        LIMIT 1
      `);
      if (!rows.length) {
        res.status(404).json({
          error: 'not_found',
          message: `Policy ${policyId} not found`,
        });
        return;
      }
      const r = rows[0];
      res.json({
        policyId: r.policy_id,
        title: r.title,
        category: r.category,
        owner: r.owner,
        version: r.version,
        content: r.content ?? '',
      });
    } catch (error) {
      console.error('[/api/policies/content] Error:', error);
      res.status(500).json({
        error: 'policy_content_failed',
        message: error instanceof Error ? error.message : String(error),
      });
    }
  },
);

/** Render a value as a safe SQL string literal (single quotes doubled), or NULL. */
function sqlString(v: string | null): string {
  if (v === null || v === undefined) return 'NULL';
  return `'${v.replace(/'/g, "''")}'`;
}

/** Best-effort signed-in user, from the reverse-proxy headers. */
function requestUser(req: Request): string {
  return (
    (req.headers['x-forwarded-email'] as string) ||
    (req.headers['x-forwarded-preferred-username'] as string) ||
    (req.headers['x-forwarded-user'] as string) ||
    'app-user'
  );
}

/**
 * GET /api/policies/uploads
 * Lists policies uploaded through the app. These live in the Lakebase
 * `PolicyUpload` table (the editable "in-between" table); Lakebase Change Data
 * Feed streams them down into the Delta policy table.
 */
policiesRouter.get(
  '/uploads',
  async (_req: Request, res: Response): Promise<void> => {
    try {
      const uploads = await listPolicyUploads();
      res.json({
        uploads: uploads.map((u) => ({
          id: u.id,
          policyId: u.policyId,
          docName: u.docName,
          category: u.category,
          title: u.title,
          owner: u.owner,
          version: u.version,
          effectiveDate: u.effectiveDate,
          reviewDate: u.reviewDate,
          content: u.content,
          sourceFilename: u.sourceFilename,
          uploadedBy: u.uploadedBy,
          createdAt:
            u.createdAt instanceof Date
              ? u.createdAt.toISOString()
              : String(u.createdAt),
          updatedAt:
            u.updatedAt instanceof Date
              ? u.updatedAt.toISOString()
              : String(u.updatedAt),
        })),
      });
    } catch (error) {
      console.error('[/api/policies/uploads] Error:', error);
      res.status(500).json({
        error: 'policy_uploads_failed',
        message: error instanceof Error ? error.message : String(error),
      });
    }
  },
);

/**
 * POST /api/policies/upload
 * Adds a new policy from an uploaded document. The PDF is converted to text in
 * the browser as it loads, so this endpoint receives editable text plus
 * metadata. The row is written to Lakebase (`PolicyUpload`); Lakebase Change
 * Data Feed then syncs it down to the Delta `policy_docs` table, where the
 * existing Vector Search Delta Sync index picks it up for the agent.
 */
policiesRouter.post(
  '/upload',
  async (req: Request, res: Response): Promise<void> => {
    try {
      const body = (req.body ?? {}) as {
        title?: string;
        docName?: string;
        category?: string;
        owner?: string;
        version?: string;
        effectiveDate?: string;
        reviewDate?: string;
        content?: string;
        sourceFilename?: string;
      };

      const title = typeof body.title === 'string' ? body.title.trim() : '';
      const content =
        typeof body.content === 'string' ? body.content.trim() : '';
      if (!title) {
        res
          .status(400)
          .json({ error: 'invalid_request', message: 'title is required' });
        return;
      }
      if (!content) {
        res.status(400).json({
          error: 'invalid_request',
          message: 'content is required (no text extracted from the document)',
        });
        return;
      }

      // doc_name is NOT NULL: derive a slug from the title when not supplied.
      const docName =
        (typeof body.docName === 'string' && body.docName.trim()) ||
        title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '_')
          .replace(/^_+|_+$/g, '')
          .slice(0, 80) ||
        'uploaded_policy';

      const clean = (v: unknown): string | null =>
        typeof v === 'string' && v.trim() ? v.trim() : null;

      const saved = await savePolicyUpload({
        docName,
        category: clean(body.category) ?? 'Uncategorized',
        title,
        owner: clean(body.owner),
        version: clean(body.version) ?? '1.0',
        effectiveDate: clean(body.effectiveDate),
        reviewDate: clean(body.reviewDate),
        content,
        sourceFilename: clean(body.sourceFilename),
        uploadedBy: requestUser(req),
      });

      res.json({
        ok: true,
        policy: {
          id: saved.id,
          policyId: saved.policyId,
          docName: saved.docName,
          category: saved.category,
          title: saved.title,
          owner: saved.owner,
          version: saved.version,
        },
        syncedVia: 'lakebase-cdf',
      });
    } catch (error) {
      console.error('[/api/policies/upload] Error:', error);
      res.status(500).json({
        error: 'policy_upload_failed',
        message: error instanceof Error ? error.message : String(error),
      });
    }
  },
);

/**
 * PUT /api/policies/content/:policyId
 * Edits a policy's Markdown text. Uploaded policies (UPL-###) are edited in the
 * Lakebase `PolicyUpload` table so the change flows back to Delta through CDF;
 * seed policies that only exist in Delta are updated directly via the warehouse.
 */
policiesRouter.put(
  '/content/:policyId',
  async (req: Request, res: Response): Promise<void> => {
    try {
      const policyId = String(req.params.policyId ?? '');
      const { content } = (req.body ?? {}) as { content?: string };
      if (!policyId) {
        res
          .status(400)
          .json({ error: 'invalid_request', message: 'policyId is required' });
        return;
      }
      if (typeof content !== 'string') {
        res.status(400).json({
          error: 'invalid_request',
          message: 'content (string) is required',
        });
        return;
      }

      // Prefer the Lakebase intermediate row so the edit re-syncs via CDF.
      const updated = await updatePolicyUploadContent(policyId, content);
      if (updated) {
        res.json({ ok: true, policyId, syncedVia: 'lakebase-cdf' });
        return;
      }

      // Seed policy that only lives in Delta: edit it directly.
      await runSql(`
        UPDATE ${POLICIES_TABLE}
        SET content = ${sqlString(content)}
        WHERE policy_id = ${sqlString(policyId)}
      `);

      res.json({ ok: true, policyId, syncedVia: 'delta' });
    } catch (error) {
      console.error('[/api/policies/content PUT] Error:', error);
      res.status(500).json({
        error: 'policy_content_update_failed',
        message: error instanceof Error ? error.message : String(error),
      });
    }
  },
);

/**
 * POST /api/policies/review
 * Records a review decision (approved | changes_requested + optional comment):
 *  1. writes the decision to Lakebase (transactional audit log), then
 *  2. writes the latest decision back to the Delta policy table.
 */
policiesRouter.post(
  '/review',
  async (req: Request, res: Response): Promise<void> => {
    try {
      const { policyId, decision, comment } = (req.body ?? {}) as {
        policyId?: string;
        decision?: string;
        comment?: string;
      };

      if (typeof policyId !== 'string' || !policyId) {
        res
          .status(400)
          .json({ error: 'invalid_request', message: 'policyId is required' });
        return;
      }
      if (decision !== 'approved' && decision !== 'changes_requested') {
        res.status(400).json({
          error: 'invalid_request',
          message: "decision must be 'approved' or 'changes_requested'",
        });
        return;
      }

      const commentStr =
        typeof comment === 'string' && comment.trim() ? comment.trim() : null;
      const reviewer = requestUser(req);

      // 1) Persist to Lakebase (transactional audit log).
      const saved = await savePolicyReview({
        policyId,
        decision,
        comment: commentStr,
        reviewer,
      });

      // 2) Write the latest decision back to the Delta policy table.
      const reviewStatus =
        decision === 'approved' ? 'Approved' : 'Changes requested';
      // Approving resets the review clock so the policy is no longer overdue;
      // requesting changes leaves the (likely overdue) review date in place.
      const reviewDateClause =
        decision === 'approved'
          ? `, review_date = ADD_MONTHS(current_date(), ${REVIEW_CYCLE_MONTHS})`
          : '';
      let deltaError: string | null = null;
      try {
        await runSql(`
          UPDATE ${POLICIES_TABLE}
          SET review_status  = ${sqlString(reviewStatus)},
              review_comment = ${sqlString(commentStr)},
              reviewed_by    = ${sqlString(reviewer)},
              reviewed_at    = current_timestamp()${reviewDateClause}
          WHERE policy_id = ${sqlString(policyId)}
        `);
      } catch (e) {
        deltaError = e instanceof Error ? e.message : String(e);
        console.error('[/api/policies/review] Delta write-back failed:', e);
      }

      res.json({
        ok: true,
        review: {
          id: saved.id,
          policyId,
          decision,
          reviewStatus,
          comment: commentStr,
          reviewer,
          createdAt: saved.createdAt,
        },
        persistedTo: deltaError ? ['lakebase'] : ['lakebase', 'delta'],
        deltaError,
      });
    } catch (error) {
      console.error('[/api/policies/review] Error:', error);
      res.status(500).json({
        error: 'policy_review_failed',
        message: error instanceof Error ? error.message : String(error),
      });
    }
  },
);

export default policiesRouter;
