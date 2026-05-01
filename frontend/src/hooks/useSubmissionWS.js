import { useEffect, useRef, useState } from 'react'

const TERMINAL = new Set([
  'ACCEPTED','WRONG_ANSWER','TIME_LIMIT_EXCEEDED',
  'MEMORY_LIMIT_EXCEEDED','COMPILATION_ERROR','RUNTIME_ERROR','INTERNAL_ERROR'
])

export function useSubmissionWS(submissionId) {
  const [status, setStatus]   = useState(null)
  const [verdict, setVerdict] = useState(null)
  const [meta, setMeta]       = useState({})
  const [done, setDone]       = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!submissionId) return

    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host  = window.location.host
    const ws    = new WebSocket(`${proto}://${host}/api/submissions/ws/${submissionId}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.error) return
      setStatus(data.status)
      setVerdict(data.verdict)
      setMeta({
        runtime_ms:        data.runtime_ms,
        memory_kb:         data.memory_kb,
        test_cases_passed: data.test_cases_passed,
        test_cases_total:  data.test_cases_total,
      })
      if (TERMINAL.has(data.status)) setDone(true)
    }

    ws.onerror = () => setDone(true)

    return () => ws.close()
  }, [submissionId])

  return { status, verdict, meta, done }
}
