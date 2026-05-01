import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { Terminal } from 'lucide-react'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(form.username, form.password)
      toast.success('Welcome back!')
      navigate('/problems')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-slide-in">
        <div className="text-center mb-8">
          <Terminal size={28} className="text-judge-accent mx-auto mb-3" />
          <h1 className="font-display text-2xl text-judge-text font-bold">SIGN IN</h1>
          <p className="text-judge-subtext text-sm mt-1">Access the judge system</p>
        </div>

        <div className="card p-6">
          <form onSubmit={handle} className="space-y-4">
            <div>
              <label className="block text-xs font-display text-judge-subtext mb-1.5">USERNAME</label>
              <input
                type="text"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                className="w-full bg-judge-bg border border-judge-border rounded px-3 py-2.5 text-sm text-judge-text
                           focus:outline-none focus:border-judge-accent transition-colors font-code"
                placeholder="username"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-display text-judge-subtext mb-1.5">PASSWORD</label>
              <input
                type="password"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                className="w-full bg-judge-bg border border-judge-border rounded px-3 py-2.5 text-sm text-judge-text
                           focus:outline-none focus:border-judge-accent transition-colors font-code"
                placeholder="••••••••"
                required
              />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
              {loading ? 'Signing in…' : 'Sign In →'}
            </button>
          </form>
        </div>

        <p className="text-center text-judge-subtext text-sm mt-4">
          No account?{' '}
          <Link to="/register" className="text-judge-accent hover:underline">Register</Link>
        </p>
      </div>
    </div>
  )
}
