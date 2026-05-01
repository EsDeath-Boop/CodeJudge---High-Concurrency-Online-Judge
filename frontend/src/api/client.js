import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Attach JWT on every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto-logout on 401
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ───────────────────────────────────────────────────────────────────────
export const register = (data) => api.post('/auth/register', data)
export const login    = (username, password) => {
  const form = new URLSearchParams({ username, password })
  return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
}

// ── Problems ───────────────────────────────────────────────────────────────────
export const getProblems   = (params) => api.get('/problems', { params })
export const getProblem    = (slug)   => api.get(`/problems/${slug}`)
export const createProblem = (data)   => api.post('/problems', data)

// ── Submissions ────────────────────────────────────────────────────────────────
export const submit          = (data)   => api.post('/submissions', data)
export const getSubmission   = (id)     => api.get(`/submissions/${id}`)
export const getSubmissions  = (params) => api.get('/submissions', { params })

// ── Test Cases ─────────────────────────────────────────────────────────────────
export const getTestCases   = (pid)       => api.get(`/problems/${pid}/testcases`)
export const addTestCase    = (pid, data) => api.post(`/problems/${pid}/testcases`, data)
export const deleteTestCase = (pid, tcid) => api.delete(`/problems/${pid}/testcases/${tcid}`)
export const bulkImport     = (pid, file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/problems/${pid}/testcases/bulk`, form)
}

// ── Leaderboard ────────────────────────────────────────────────────────────────
export const getGlobalLeaderboard  = (params) => api.get('/leaderboard/global', { params })
export const getProblemLeaderboard = (pid)     => api.get(`/leaderboard/problem/${pid}`)
export const getMyStats            = ()        => api.get('/leaderboard/me')
export const getMyProblemRank      = (pid)     => api.get(`/leaderboard/problem/${pid}/my-rank`)

export default api
