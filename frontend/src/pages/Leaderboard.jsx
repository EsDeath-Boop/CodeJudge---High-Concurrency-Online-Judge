import { useState, useEffect } from 'react'
import { getGlobalLeaderboard } from '../api/client'
import { Trophy, Loader, Medal } from 'lucide-react'

const RANK_COLORS = ['text-yellow-400', 'text-slate-300', 'text-amber-600']

export default function Leaderboard() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getGlobalLeaderboard({ limit: 50 })
      .then(r => setEntries(r.data))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 animate-fade-in">
      <div className="flex items-center gap-3 mb-8">
        <Trophy size={22} className="text-judge-accent" />
        <div>
          <h1 className="font-display text-3xl text-judge-text font-bold">LEADERBOARD</h1>
          <p className="text-judge-subtext text-sm">Ranked by score — Easy 10pts · Medium 20pts · Hard 40pts</p>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="grid grid-cols-[3rem_1fr_7rem_7rem_7rem_6rem] text-xs font-display text-judge-muted border-b border-judge-border px-4 py-3">
          <span>RANK</span>
          <span>USER</span>
          <span>SOLVED</span>
          <span>SUBMISSIONS</span>
          <span>ACC. RATE</span>
          <span className="text-right">SCORE</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader size={20} className="text-judge-accent animate-spin" />
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-20 text-judge-subtext text-sm">
            No solvers yet — be the first!
          </div>
        ) : (
          entries.map((e) => (
            <div
              key={e.rank}
              className="grid grid-cols-[3rem_1fr_7rem_7rem_7rem_6rem] items-center px-4 py-3.5
                         border-b border-judge-border/50 hover:bg-judge-accent/5 transition-colors"
            >
              <span className={`font-display text-sm font-bold ${RANK_COLORS[e.rank - 1] || 'text-judge-muted'}`}>
                {e.rank <= 3 ? <Medal size={16} className="inline" /> : `#${e.rank}`}
              </span>
              <span className="text-judge-text text-sm font-medium">{e.username}</span>
              <span className="text-judge-accent font-code text-sm">{e.problems_solved}</span>
              <span className="text-judge-subtext text-sm">{e.total_submissions}</span>
              <span className="text-judge-subtext text-sm">
                {(e.acceptance_rate * 100).toFixed(1)}%
              </span>
              <span className="text-right font-display text-judge-accent font-bold text-sm">
                {e.score}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
