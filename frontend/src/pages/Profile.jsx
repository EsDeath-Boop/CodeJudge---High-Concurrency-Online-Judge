import { useState, useEffect } from 'react'
import { getMyStats, getSubmissions } from '../api/client'
import { useAuth } from '../context/AuthContext'
import VerdictBadge from '../components/VerdictBadge'
import { User, Trophy, Target, Zap, Loader } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

function StatCard({ icon: Icon, label, value, color = 'text-judge-accent' }) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 mb-1">
        <Icon size={13} className={color} />
        <span className="text-xs font-display text-judge-muted">{label}</span>
      </div>
      <div className={`font-display text-2xl font-bold ${color}`}>{value}</div>
    </div>
  )
}

export default function Profile() {
  const { user } = useAuth()
  const [stats, setStats]           = useState(null)
  const [submissions, setSubmissions] = useState([])
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    Promise.all([
      getMyStats().then(r => setStats(r.data)).catch(() => {}),
      getSubmissions({ limit: 20 }).then(r => setSubmissions(r.data)).catch(() => {}),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader className="text-judge-accent animate-spin" />
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 animate-fade-in space-y-8">

      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-judge-accent/10 border border-judge-accent/30 flex items-center justify-center">
          <User size={24} className="text-judge-accent" />
        </div>
        <div>
          <h1 className="font-display text-2xl text-judge-text font-bold">{user?.username}</h1>
          {stats?.global_rank && (
            <p className="text-judge-subtext text-sm">Global Rank #{stats.global_rank}</p>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard icon={Target} label="PROBLEMS SOLVED" value={stats?.problems_solved ?? 0} />
        <StatCard icon={Zap}    label="TOTAL SUBMISSIONS" value={stats?.total_submissions ?? 0} color="text-judge-accent2" />
        <StatCard icon={Trophy} label="SCORE" value={stats?.score ?? 0} color="text-yellow-400" />
        <StatCard
          icon={Target}
          label="ACCEPTANCE"
          value={`${((stats?.acceptance_rate ?? 0) * 100).toFixed(1)}%`}
          color="text-emerald-400"
        />
      </div>

      {/* Recent submissions */}
      <div>
        <h2 className="font-display text-sm text-judge-subtext mb-3">RECENT SUBMISSIONS</h2>
        <div className="card overflow-hidden">
          <div className="grid grid-cols-[2rem_1fr_6rem_6rem_6rem] text-xs font-display text-judge-muted border-b border-judge-border px-4 py-3">
            <span>#</span>
            <span>PROBLEM</span>
            <span>LANG</span>
            <span>VERDICT</span>
            <span className="text-right">TIME</span>
          </div>

          {submissions.length === 0 ? (
            <div className="text-center py-12 text-judge-subtext text-sm">No submissions yet</div>
          ) : (
            submissions.map((s) => (
              <div
                key={s.id}
                className="grid grid-cols-[2rem_1fr_6rem_6rem_6rem] items-center px-4 py-3
                           border-b border-judge-border/50 hover:bg-judge-accent/5 transition-colors"
              >
                <span className="text-judge-muted font-code text-xs">{s.id}</span>
                <span className="text-judge-text text-sm">Problem #{s.problem_id}</span>
                <span className="text-judge-subtext text-xs font-code">{s.language}</span>
                <VerdictBadge verdict={s.verdict || s.status} />
                <span className="text-right text-judge-muted text-xs">
                  {s.created_at
                    ? formatDistanceToNow(new Date(s.created_at), { addSuffix: true })
                    : '—'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
