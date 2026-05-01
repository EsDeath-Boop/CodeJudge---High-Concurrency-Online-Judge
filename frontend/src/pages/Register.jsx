import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { Terminal } from 'lucide-react'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register(form.username, form.email, form.password)
      toast.success('Account created!')
      navigate('/problems')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const field = (key, label, type = 'text', placeholder = '') => (
    <div>
      <label className="block text-xs font-display text-judge-subtext mb-1.5">{label}</label>
      <input
        type={type}
        value={form[key]}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        className="w-full bg-judge-bg border border-judge-border rounded px-3 py-2.5 text-sm text-judge-text
                   focus:outline-none focus:border-judge-accent transition-colors font-code"
        placeholder={placeholder}
        required
      />
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-slide-in">
        <div className="text-center mb-8">
          <Terminal size={28} className="text-judge-accent mx-auto mb-3" />
          <h1 className="font-display text-2xl text-judge-text font-bold">CREATE ACCOUNT</h1>
          <p className="text-judge-subtext text-sm mt-1">Join the judge system</p>
        </div>

        <div className="card p-6">
          <form onSubmit={handle} className="space-y-4">
            {field('username', 'USERNAME', 'text', 'coder42')}
            {field('email',    'EMAIL',    'email','you@example.com')}
            {field('password', 'PASSWORD', 'password','••••••••')}
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
              {loading ? 'Creating…' : 'Create Account →'}
            </button>
          </form>
        </div>

        <p className="text-center text-judge-subtext text-sm mt-4">
          Have an account?{' '}
          <Link to="/login" className="text-judge-accent hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
