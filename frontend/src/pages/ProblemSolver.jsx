import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { getProblem, getTestCases, submit, getProblemLeaderboard } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useSubmissionWS } from '../hooks/useSubmissionWS'
import VerdictBadge from '../components/VerdictBadge'
import toast from 'react-hot-toast'
import { Play, Loader, Clock, MemoryStick, Trophy, ChevronDown, ChevronUp } from 'lucide-react'

const LANGS = [
  { id: 'cpp',    label: 'C++',    monaco: 'cpp',    starter: '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // your code here\n    return 0;\n}\n' },
  { id: 'python', label: 'Python', monaco: 'python', starter: '# your code here\n' },
  { id: 'java',   label: 'Java',   monaco: 'java',   starter: 'import java.util.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // your code here\n    }\n}\n' },
]

function VerdictPanel({ submissionId }) {
  const { status, verdict, meta, done } = useSubmissionWS(submissionId)
  if (!submissionId) return null

  return (
    <div className={`card p-4 border transition-colors duration-500
      ${verdict === 'ACCEPTED' ? 'border-judge-accent/40' :
        (done && verdict) ? 'border-judge-danger/30' : 'border-judge-border'}`}>

      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-display text-judge-subtext">VERDICT</span>
        {!done && <Loader size={12} className="text-judge-accent animate-spin" />}
      </div>

      <VerdictBadge verdict={verdict || status || 'PENDING'} size="lg" />

      {done && meta.runtime_ms != null && (
        <div className="flex gap-4 mt-4 pt-4 border-t border-judge-border">
          <div className="flex items-center gap-1.5 text-sm text-judge-subtext">
            <Clock size={13} className="text-judge-accent" />
            <span>{meta.runtime_ms?.toFixed(1)} ms</span>
          </div>
          <div className="flex items-center gap-1.5 text-sm text-judge-subtext">
            <MemoryStick size={13} className="text-judge-accent2" />
            <span>{meta.memory_kb?.toFixed(0)} KB</span>
          </div>
          <div className="text-sm text-judge-subtext ml-auto">
            {meta.test_cases_passed}/{meta.test_cases_total} cases
          </div>
        </div>
      )}
    </div>
  )
}

export default function ProblemSolver() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [problem, setProblem]       = useState(null)
  const [testCases, setTestCases]   = useState([])
  const [langIdx, setLangIdx]       = useState(0)
  const [code, setCode]             = useState(LANGS[0].starter)
  const [submitting, setSubmitting] = useState(false)
  const [submissionId, setSubId]    = useState(null)
  const [leaders, setLeaders]       = useState([])
  const [showLeaders, setShowLeaders] = useState(false)
  const [showSamples, setShowSamples] = useState(true)

  const lang = LANGS[langIdx]

  useEffect(() => {
    getProblem(slug)
      .then(r => setProblem(r.data))
      .catch(() => navigate('/problems'))
  }, [slug])

  useEffect(() => {
    if (!problem) return
    getTestCases(problem.id)
      .then(r => setTestCases(r.data.filter(tc => tc.is_sample)))
      .catch(() => {})
    getProblemLeaderboard(problem.id)
      .then(r => setLeaders(r.data.slice(0, 5)))
      .catch(() => {})
  }, [problem])

  const handleSubmit = async () => {
    if (!user) { navigate('/login'); return }
    setSubmitting(true)
    setSubId(null)
    try {
      const { data } = await submit({
        problem_id: problem.id,
        language: lang.id,
        code,
      })
      setSubId(data.id)
      toast.success(`Submission #${data.id} queued`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  if (!problem) return (
    <div className="flex items-center justify-center h-64">
      <Loader className="text-judge-accent animate-spin" />
    </div>
  )

  return (
    <div className="h-[calc(100vh-56px)] flex overflow-hidden">

      {/* Left: problem statement */}
      <div className="w-[40%] min-w-80 border-r border-judge-border overflow-y-auto p-6 space-y-5">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className={`tag-${problem.difficulty}`}>{problem.difficulty}</span>
            <span className="text-judge-muted text-xs font-code">
              {problem.time_limit}s · {problem.memory_limit}MB
            </span>
          </div>
          <h1 className="font-display text-xl text-judge-text font-bold">{problem.title}</h1>
        </div>

        <div className="text-sm text-judge-subtext leading-relaxed whitespace-pre-wrap">
          {problem.description}
        </div>

        {/* Sample cases */}
        {testCases.length > 0 && (
          <div>
            <button
              onClick={() => setShowSamples(s => !s)}
              className="flex items-center gap-2 text-xs font-display text-judge-subtext hover:text-judge-accent mb-2 transition-colors"
            >
              {showSamples ? <ChevronUp size={12}/> : <ChevronDown size={12}/>}
              SAMPLE CASES ({testCases.length})
            </button>
            {showSamples && testCases.map((tc, i) => (
              <div key={tc.id} className="mb-3">
                <p className="text-xs font-display text-judge-muted mb-1">SAMPLE {i + 1}</p>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <p className="text-xs text-judge-muted mb-1">Input</p>
                    <pre className="bg-judge-bg border border-judge-border rounded p-2 text-xs font-code text-judge-text overflow-x-auto">
                      {tc.input_data || '(empty)'}
                    </pre>
                  </div>
                  <div>
                    <p className="text-xs text-judge-muted mb-1">Output</p>
                    <pre className="bg-judge-bg border border-judge-border rounded p-2 text-xs font-code text-judge-text overflow-x-auto">
                      {tc.expected_output}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Mini leaderboard */}
        {leaders.length > 0 && (
          <div>
            <button
              onClick={() => setShowLeaders(s => !s)}
              className="flex items-center gap-2 text-xs font-display text-judge-subtext hover:text-judge-accent mb-2 transition-colors"
            >
              <Trophy size={12} className="text-judge-accent" />
              TOP SOLVERS
              {showLeaders ? <ChevronUp size={12}/> : <ChevronDown size={12}/>}
            </button>
            {showLeaders && (
              <div className="card overflow-hidden">
                {leaders.map((l, i) => (
                  <div key={i} className="flex items-center gap-3 px-3 py-2 border-b border-judge-border/50 last:border-0">
                    <span className="text-xs font-display text-judge-muted w-4">#{l.rank}</span>
                    <span className="text-xs text-judge-text flex-1">{l.username}</span>
                    <span className="text-xs font-code text-judge-accent">{l.runtime_ms}ms</span>
                    <span className="text-xs text-judge-muted">{l.language}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right: editor + verdict */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Editor toolbar */}
        <div className="flex items-center gap-3 px-4 py-2 border-b border-judge-border bg-judge-surface">
          <div className="flex gap-1">
            {LANGS.map((l, i) => (
              <button
                key={l.id}
                onClick={() => { setLangIdx(i); setCode(l.starter) }}
                className={`px-3 py-1.5 rounded text-xs font-display transition-all
                  ${langIdx === i
                    ? 'bg-judge-accent text-judge-bg font-bold'
                    : 'text-judge-subtext hover:text-judge-accent'
                  }`}
              >
                {l.label}
              </button>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="btn-primary flex items-center gap-2 py-1.5 px-4 text-xs"
            >
              {submitting
                ? <><Loader size={12} className="animate-spin" /> Submitting…</>
                : <><Play size={12} /> Submit</>
              }
            </button>
          </div>
        </div>

        {/* Monaco editor */}
        <div className="flex-1 overflow-hidden">
          <Editor
            height="100%"
            language={lang.monaco}
            value={code}
            onChange={v => setCode(v || '')}
            theme="vs-dark"
            options={{
              fontSize: 13,
              fontFamily: '"Fira Code", monospace',
              fontLigatures: true,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              lineNumbers: 'on',
              wordWrap: 'on',
              tabSize: 4,
              renderWhitespace: 'selection',
              smoothScrolling: true,
            }}
          />
        </div>

        {/* Verdict panel */}
        <div className="p-4 border-t border-judge-border bg-judge-surface">
          {submissionId
            ? <VerdictPanel submissionId={submissionId} />
            : (
              <div className="text-center text-judge-muted text-sm font-display py-2">
                Submit your solution to see the verdict
              </div>
            )
          }
        </div>
      </div>
    </div>
  )
}
