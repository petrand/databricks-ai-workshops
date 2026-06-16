import {
  Router,
  type Request,
  type Response,
  type Router as RouterType,
} from 'express';
import { getDatabricksToken, getCachedCliHost } from '@chat-template/auth';
import { getHostUrl } from '@chat-template/utils';

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
          END AS status
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

export default policiesRouter;
