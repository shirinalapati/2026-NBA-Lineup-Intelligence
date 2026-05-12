import { Link, NavLink } from 'react-router-dom'
import { Moon, Sun, BarChart3, LayoutGrid, Shuffle, Sparkles, TrendingUp, Info } from 'lucide-react'
import { clsx } from 'clsx'
import { useEffect, useState } from 'react'

const nav = [
  { to: '/', label: 'About', icon: Info },
  { to: '/overview', label: 'Overview', icon: LayoutGrid },
  { to: '/leaderboard', label: 'Leaderboard', icon: BarChart3 },
  { to: '/explorer', label: 'Team explorer', icon: Sparkles },
  { to: '/underrated', label: 'Underrated', icon: TrendingUp },
  { to: '/simulator', label: 'Simulator', icon: Shuffle },
]

export function Layout({ children }: { children: React.ReactNode }) {
  const [dark, setDark] = useState(true)
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-200/80 dark:border-court-700 bg-white/80 dark:bg-court-900/90 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between gap-4 h-16">
          <Link to="/" className="flex items-baseline gap-2 group">
            <span className="font-display text-xl sm:text-2xl text-court-950 dark:text-white tracking-tight">
              Lineup Intelligence
            </span>
            <span className="hidden sm:inline text-[10px] font-mono uppercase tracking-widest text-court-line dark:text-court-line/90">
              2025-26 NBA
            </span>
          </Link>
          <nav className="hidden lg:flex items-center gap-1">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  clsx(
                    'px-3 py-1.5 rounded-md text-sm font-medium flex items-center gap-1.5 transition-colors',
                    isActive
                      ? 'bg-court-accent/15 text-court-accent'
                      : 'text-slate-600 dark:text-slate-400 hover:text-court-950 dark:hover:text-white',
                  )
                }
              >
                <Icon className="w-3.5 h-3.5 opacity-80" />
                {label}
              </NavLink>
            ))}
          </nav>
          <button
            type="button"
            onClick={() => setDark((d) => !d)}
            className="p-2 rounded-lg border border-slate-200 dark:border-court-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-court-800"
            aria-label="Toggle theme"
          >
            {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
        <div className="lg:hidden border-t border-slate-200/80 dark:border-court-700 overflow-x-auto">
          <div className="flex gap-1 px-4 py-2">
            {nav.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  clsx(
                    'whitespace-nowrap px-3 py-1 rounded-full text-xs font-medium',
                    isActive ? 'bg-court-accent/20 text-court-accent' : 'text-slate-500',
                  )
                }
              >
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">{children}</main>
      <footer className="border-t border-slate-200 dark:border-court-800 py-6 text-center text-xs text-slate-500 dark:text-slate-500">
        2025-26 NBA regular season only (no playoffs / play-in) · Data via ingestion pipeline
      </footer>
    </div>
  )
}
