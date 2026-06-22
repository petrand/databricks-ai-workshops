import useSWR from 'swr';

export type PolicyStatus = 'Overdue' | 'Due soon' | 'Current';

export interface PolicyRow {
  policyId: string;
  docName: string;
  category: string;
  title: string;
  owner: string;
  version: string;
  effectiveDate: string;
  reviewDate: string;
  daysOverdue: number;
  ageDays: number;
  status: PolicyStatus;
  reviewStatus: string | null;
  reviewComment: string | null;
  reviewedBy: string | null;
  reviewedAt: string | null;
}

export type ReviewDecision = 'approved' | 'changes_requested';

export interface CategoryRow {
  category: string;
  total: number;
  overdue: number;
  dueSoon: number;
  current: number;
}

export interface PolicyComplianceData {
  generatedAt: string;
  table: string;
  summary: {
    total: number;
    overdue: number;
    dueSoon: number;
    current: number;
    staleOverYear: number;
    avgAgeDays: number;
    pctOverdue: number;
    oldestEffective: string | null;
    newestEffective: string | null;
  };
  byCategory: CategoryRow[];
  policies: PolicyRow[];
}

/** Fetch that surfaces the server's error message (e.g. warehouse not set). */
async function jsonFetcher<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.message) message = body.message;
    } catch {
      // ignore JSON parse failures
    }
    throw new Error(message);
  }
  return response.json();
}

export function usePoliciesData() {
  const { data, error, isLoading, mutate } = useSWR<PolicyComplianceData>(
    '/api/policies/compliance',
    jsonFetcher<PolicyComplianceData>,
    { revalidateOnFocus: false },
  );

  return {
    data,
    error: error as Error | undefined,
    isLoading,
    refresh: mutate,
  };
}

/** Fetch the full Markdown content for a single policy on demand. */
export async function fetchPolicyContent(
  policyId: string,
): Promise<{ policyId: string; content: string }> {
  const response = await fetch(
    `/api/policies/content/${encodeURIComponent(policyId)}`,
  );
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.message) message = body.message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  return response.json();
}

/** Update the Markdown content of an existing policy. */
export async function updatePolicyContent(
  policyId: string,
  content: string,
): Promise<{
  ok: boolean;
  policyId: string;
  syncedVia: 'lakebase-cdf' | 'delta';
}> {
  const response = await fetch(
    `/api/policies/content/${encodeURIComponent(policyId)}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    },
  );
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.message) message = body.message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  return response.json();
}

export interface UploadPolicyInput {
  title: string;
  docName?: string;
  category?: string;
  owner?: string;
  version?: string;
  effectiveDate?: string;
  reviewDate?: string;
  content: string;
  sourceFilename?: string;
}

export interface UploadedPolicy {
  id: string;
  policyId: string;
  docName: string;
  category: string | null;
  title: string;
  owner: string | null;
  version: string | null;
  effectiveDate: string | null;
  reviewDate: string | null;
  content: string;
  sourceFilename: string | null;
  uploadedBy: string;
  createdAt: string;
  updatedAt: string;
}

/** List policies uploaded through the app (the Lakebase intermediate table). */
export function useUploads() {
  const { data, error, isLoading, mutate } = useSWR<{
    uploads: UploadedPolicy[];
  }>('/api/policies/uploads', jsonFetcher<{ uploads: UploadedPolicy[] }>, {
    revalidateOnFocus: false,
  });
  return {
    uploads: data?.uploads ?? [],
    error: error as Error | undefined,
    isLoading,
    refresh: mutate,
  };
}

/** Add a new policy (from an uploaded document) to the policy table. */
export async function uploadPolicy(input: UploadPolicyInput): Promise<{
  ok: boolean;
  policy: {
    policyId: string;
    docName: string;
    category: string;
    title: string;
    owner: string | null;
    version: string;
  };
}> {
  const response = await fetch('/api/policies/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.message) message = body.message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  return response.json();
}

/** Submit a review decision; persists to Lakebase and writes back to Delta. */
export async function submitPolicyReview(input: {
  policyId: string;
  decision: ReviewDecision;
  comment: string;
}): Promise<{ persistedTo: string[]; deltaError: string | null }> {
  const response = await fetch('/api/policies/review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.message) message = body.message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  return response.json();
}
