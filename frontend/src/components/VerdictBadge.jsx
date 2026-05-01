const MAP = {
  ACCEPTED:             { label: 'Accepted',              cls: 'verdict-ac'  },
  WRONG_ANSWER:         { label: 'Wrong Answer',          cls: 'verdict-wa'  },
  TIME_LIMIT_EXCEEDED:  { label: 'Time Limit Exceeded',   cls: 'verdict-tle' },
  MEMORY_LIMIT_EXCEEDED:{ label: 'Memory Limit Exceeded', cls: 'verdict-mle' },
  COMPILATION_ERROR:    { label: 'Compilation Error',     cls: 'verdict-ce'  },
  RUNTIME_ERROR:        { label: 'Runtime Error',         cls: 'verdict-re'  },
  INTERNAL_ERROR:       { label: 'Internal Error',        cls: 'verdict-wa'  },
  PENDING:              { label: 'Pending…',              cls: 'text-judge-subtext' },
  RUNNING:              { label: 'Running…',              cls: 'text-judge-accent2 animate-pulse' },
}

export default function VerdictBadge({ verdict, size = 'md' }) {
  const { label, cls } = MAP[verdict] || { label: verdict, cls: 'text-judge-subtext' }
  const sz = size === 'lg' ? 'text-xl font-bold' : 'text-sm font-display'
  return <span className={`${cls} ${sz}`}>{label}</span>
}
