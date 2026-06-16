import { useMemo, useState } from 'react';
import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  FileText,
  RefreshCw,
} from 'lucide-react';
import {
  usePoliciesData,
  type PolicyRow,
  type PolicyStatus,
} from '@/hooks/usePoliciesData';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const STATUS_BADGE: Record<PolicyStatus, string> = {
  Overdue:
    'bg-[var(--background-danger)] text-destructive border-[var(--border-danger)]',
  'Due soon':
    'bg-[var(--background-warning)] text-[var(--warning)] border-[var(--border-warning)]',
  Current:
    'bg-[var(--background-success)] text-[var(--success)] border-[var(--border-success)]',
};

type Filter = 'all' | PolicyStatus;
const FILTERS: Filter[] = ['all', 'Overdue', 'Due soon', 'Current'];

function KpiCard({
  label,
  value,
  sub,
  icon,
  tone = 'default',
}: {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  tone?: 'default' | 'danger' | 'warning' | 'success';
}) {
  const toneColor =
    tone === 'danger'
      ? 'text-destructive'
      : tone === 'warning'
        ? 'text-[var(--warning)]'
        : tone === 'success'
          ? 'text-[var(--success)]'
          : 'text-foreground';
  return (
    <div className="flex flex-col gap-1 rounded-xl border border-border bg-card p-4">
      <div className="flex items-center justify-between text-muted-foreground">
        <span className="font-medium text-xs uppercase tracking-wide">
          {label}
        </span>
        {icon}
      </div>
      <span className={cn('font-semibold text-3xl tabular-nums', toneColor)}>
        {value}
      </span>
      {sub && <span className="text-muted-foreground text-xs">{sub}</span>}
    </div>
  );
}

/** Stacked overdue / due-soon / current bar for a category. */
function CategoryBar({
  overdue,
  dueSoon,
  current,
  total,
}: {
  overdue: number;
  dueSoon: number;
  current: number;
  total: number;
}) {
  const pct = (n: number) => (total ? `${(n / total) * 100}%` : '0%');
  return (
    <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-muted">
      {overdue > 0 && (
        <div className="bg-destructive" style={{ width: pct(overdue) }} />
      )}
      {dueSoon > 0 && (
        <div className="bg-[var(--warning)]" style={{ width: pct(dueSoon) }} />
      )}
      {current > 0 && (
        <div className="bg-[var(--success)]" style={{ width: pct(current) }} />
      )}
    </div>
  );
}

export default function DashboardPage() {
  const { data, error, isLoading, refresh } = usePoliciesData();
  const [filter, setFilter] = useState<Filter>('all');

  const filtered = useMemo<PolicyRow[]>(() => {
    if (!data) return [];
    if (filter === 'all') return data.policies;
    return data.policies.filter((p) => p.status === filter);
  }, [data, filter]);

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3 border-border border-b px-6 py-4">
        <div>
          <h1 className="font-semibold text-foreground text-lg">
            Policy Compliance
          </h1>
          <p className="text-muted-foreground text-sm">
            Review-date compliance and staleness across company policies
          </p>
        </div>
        <div className="flex items-center gap-3">
          {data && (
            <span className="hidden text-muted-foreground text-xs sm:inline">
              {data.table} · {new Date(data.generatedAt).toLocaleString()}
            </span>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => refresh()}
            disabled={isLoading}
          >
            <RefreshCw
              className={cn('mr-2 h-4 w-4', isLoading && 'animate-spin')}
            />
            Refresh
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-6 p-6">
        {/* Error */}
        {error && (
          <div className="rounded-xl border border-[var(--border-danger)] bg-[var(--background-danger)] p-4 text-destructive text-sm">
            <p className="font-medium">Couldn’t load policy data</p>
            <p className="mt-1 opacity-90">{error.message}</p>
            <p className="mt-2 text-xs opacity-75">
              Set <code>DATABRICKS_SQL_WAREHOUSE_ID</code> (and optionally{' '}
              <code>POLICIES_TABLE</code>) and make sure the policy table
              exists.
            </p>
          </div>
        )}

        {/* Loading */}
        {isLoading && !data && (
          <div className="text-muted-foreground text-sm">
            Loading policy compliance…
          </div>
        )}

        {data && (
          <>
            {/* KPIs */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <KpiCard
                label="Total policies"
                value={data.summary.total}
                icon={<FileText className="h-4 w-4" />}
              />
              <KpiCard
                label="Overdue review"
                value={data.summary.overdue}
                sub={`${data.summary.pctOverdue}% of all policies`}
                icon={<AlertTriangle className="h-4 w-4" />}
                tone="danger"
              />
              <KpiCard
                label="Due soon (90d)"
                value={data.summary.dueSoon}
                icon={<CalendarClock className="h-4 w-4" />}
                tone="warning"
              />
              <KpiCard
                label="Avg age"
                value={`${data.summary.avgAgeDays}d`}
                sub={`${data.summary.staleOverYear} older than 1 year`}
                icon={<CheckCircle2 className="h-4 w-4" />}
              />
            </div>

            {/* By category */}
            <div className="rounded-xl border border-border bg-card p-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="font-semibold text-foreground text-sm">
                  Review status by category
                </h2>
                <div className="flex items-center gap-3 text-muted-foreground text-xs">
                  <Legend className="bg-destructive" label="Overdue" />
                  <Legend className="bg-[var(--warning)]" label="Due soon" />
                  <Legend className="bg-[var(--success)]" label="Current" />
                </div>
              </div>
              <div className="flex flex-col gap-3">
                {data.byCategory.map((c) => (
                  <div
                    key={c.category}
                    className="grid grid-cols-[minmax(0,1fr)_2fr_auto] items-center gap-3"
                  >
                    <span className="truncate text-foreground text-sm">
                      {c.category}
                    </span>
                    <CategoryBar
                      overdue={c.overdue}
                      dueSoon={c.dueSoon}
                      current={c.current}
                      total={c.total}
                    />
                    <span className="text-muted-foreground text-xs tabular-nums">
                      <span className="font-medium text-destructive">
                        {c.overdue}
                      </span>{' '}
                      / {c.total}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Policy table */}
            <div className="rounded-xl border border-border bg-card">
              <div className="flex flex-wrap items-center justify-between gap-2 border-border border-b p-4">
                <h2 className="font-semibold text-foreground text-sm">
                  Policies ({filtered.length})
                </h2>
                <div className="flex gap-1">
                  {FILTERS.map((f) => (
                    <button
                      type="button"
                      key={f}
                      onClick={() => setFilter(f)}
                      className={cn(
                        'rounded-md px-2.5 py-1 font-medium text-xs capitalize transition-colors',
                        filter === f
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-muted',
                      )}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>
              <div className="max-h-[480px] overflow-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-card text-muted-foreground text-xs uppercase tracking-wide">
                    <tr className="border-border border-b">
                      <th className="px-4 py-2 text-left font-medium">ID</th>
                      <th className="px-4 py-2 text-left font-medium">Title</th>
                      <th className="px-4 py-2 text-left font-medium">Owner</th>
                      <th className="px-4 py-2 text-left font-medium">
                        Review date
                      </th>
                      <th className="px-4 py-2 text-right font-medium">
                        Days overdue
                      </th>
                      <th className="px-4 py-2 text-left font-medium">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((p) => (
                      <tr
                        key={p.policyId}
                        className="border-border border-b last:border-0 hover:bg-muted/40"
                      >
                        <td className="whitespace-nowrap px-4 py-2 font-mono text-muted-foreground text-xs">
                          {p.policyId}
                        </td>
                        <td className="px-4 py-2 text-foreground">
                          <span className="line-clamp-1">{p.title}</span>
                          <span className="text-muted-foreground text-xs">
                            {p.category}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-muted-foreground">
                          {p.owner}
                        </td>
                        <td className="whitespace-nowrap px-4 py-2 text-muted-foreground tabular-nums">
                          {p.reviewDate}
                        </td>
                        <td className="px-4 py-2 text-right tabular-nums">
                          {p.daysOverdue > 0 ? (
                            <span className="font-medium text-destructive">
                              {p.daysOverdue}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </td>
                        <td className="px-4 py-2">
                          <Badge
                            variant="outline"
                            className={STATUS_BADGE[p.status]}
                          >
                            {p.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                    {filtered.length === 0 && (
                      <tr>
                        <td
                          colSpan={6}
                          className="px-4 py-8 text-center text-muted-foreground text-sm"
                        >
                          No policies match this filter.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Legend({ className, label }: { className: string; label: string }) {
  return (
    <span className="flex items-center gap-1">
      <span
        className={cn('inline-block h-2.5 w-2.5 rounded-full', className)}
      />
      {label}
    </span>
  );
}
