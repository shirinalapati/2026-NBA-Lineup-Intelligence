import type { ReactNode } from 'react'
import { clsx } from 'clsx'

export function StatCard({
  label,
  value,
  rank,
  hint,
  className,
}: {
  label: string
  value: string
  rank?: string | null
  hint?: ReactNode
  className?: string
}) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-slate-200 dark:border-court-700 bg-white dark:bg-court-850 p-5 shadow-sm',
        className,
      )}
    >
      <p className="text-xs font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-2 font-display text-3xl text-court-950 dark:text-white">{value}</p>
      {rank != null && rank !== '' && (
        <p className="mt-1 text-sm font-medium tabular-nums text-court-accent">{rank}</p>
      )}
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  )
}
