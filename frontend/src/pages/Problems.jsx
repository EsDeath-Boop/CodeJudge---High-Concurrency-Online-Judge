import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getProblems } from '../api/client'
import { Search, ChevronRight, Loader } from 'lucide-react'

const DIFFS = ['all', 'easy', 'medium', 'hard']

export default function Problems() {
  const [problems, setProblems]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [difficulty, setDiff]     = useState('all')
  const [search, setSearch]       = useState('')

  useEffect(() => {
    setLoading(true)
    const params = difficulty !== 'all' ? { difficulty } : {}
    getProblems(params)
      .then(r => setProblems(r.data))
      .finally(() => setLoading(false))
  }, [difficulty])

  const filtered = problems.filter(p =>
    p.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 animate-fade-in">
      {/* Header */}
      <div className="flex items-end justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl text-judge-text font-bold">PROBLEMS</h1>
          <p className="text-judge-subtext text-sm mt-1">{problems.length} problems available</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-judge-muted" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search problems…"
            className="w-full bg-judge-surface border border-judge-border rounded pl-9 pr-3 py-2.5
                       text-sm text-judge-text focus:outline-none focus:border-judge-accent transition-colors"
          />
        </div>
        <div className="flex gap-2">
          {DIFFS.map(d => (
            <button
              key={d}
              onClick={() => setDiff(d)}
              className={`px-4 py-2 rounded text-xs font-display transition-all
                ${difficulty === d
                  ? 'bg-judge-accent text-judge-bg font-bold'
                  : 'border border-judge-border text-judge-subtext hover:border-judge-accent hover:text-judge-accent'
                }`}
            >
              {d.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="grid grid-cols-[3rem_1fr_6rem_8rem] text-xs font-display text-judge-muted border-b border-judge-border px-4 py-3">
          <span>#</span>
          <span>TITLE</span>
          <span>DIFFICULTY</span>
          <span className="text-right">ACTION</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader size={20} className="text-judge-accent animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-judge-subtext text-sm">No problems found</div>
        ) : (
          filtered.map((p, i) => (
            <Link
              key={p.id}
              to={`/problems/${p.slug}`}
              className="grid grid-cols-[3rem_1fr_6rem_8rem] items-center px-4 py-4
                         border-b border-judge-border/50 hover:bg-judge-accent/5
                         transition-colors group"
            >
              <span className="text-judge-muted font-code text-sm">{i + 1}</span>
              <span className="text-judge-text text-sm group-hover:text-judge-accent transition-colors">
                {p.title}
              </span>
              <span>
                <span className={`tag-${p.difficulty}`}>{p.difficulty}</span>
              </span>
              <div className="flex justify-end">
                <ChevronRight size={14} className="text-judge-muted group-hover:text-judge-accent transition-colors" />
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  )
}
