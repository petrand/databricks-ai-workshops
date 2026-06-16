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
}

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
async function policiesFetcher(url: string): Promise<PolicyComplianceData> {
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
    policiesFetcher,
    { revalidateOnFocus: false },
  );

  return {
    data,
    error: error as Error | undefined,
    isLoading,
    refresh: mutate,
  };
}
