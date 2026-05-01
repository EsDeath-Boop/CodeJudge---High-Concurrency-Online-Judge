import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Terminal, Trophy, Code2, LogOut, User } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const nav = [
    { to: '/problems', label: 'Problems', icon: Code2 },
    { to: '/leaderboard', label: 'Leaderboard', icon: Trophy },
  ]

  const isActive = (to) => pathname.startsWith(to)

  return (
    <nav className="scanlines relative border-b border-judge-border bg-judge-surface/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 flex items-center h-14 gap-6">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 mr-4">
          <Terminal size={18} className="text-judge-accent" />
          <span className="font-display text-judge-accent text-sm font-bold tracking-wider animate-glow">
            CODEJUDGE
          </span>
        </Link>

        {/* Nav links */}
        {nav.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            className={`flex items-center gap-1.5 text-sm font-display transition-colors duration-150
              ${isActive(to)
                ? 'text-judge-accent'
                : 'text-judge-subtext hover:text-judge-text'
              }`}
          >
            <Icon size={14} />
            {label}
          </Link>
        ))}

        <div className="ml-auto flex items-center gap-3">
          {user ? (
            <>
              <Link to="/profile" className="flex items-center gap-1.5 text-sm text-judge-subtext hover:text-judge-accent transition-colors">
                <User size={14} />
                <span className="font-display">{user.username}</span>
              </Link>
              <button
                onClick={() => { logout(); navigate('/') }}
                className="flex items-center gap-1 text-judge-muted hover:text-judge-danger transition-colors text-sm"
              >
                <LogOut size={14} />
              </button>
            </>
          ) : (
            <>
              <Link to="/login"    className="btn-ghost text-xs py-1.5 px-4">Login</Link>
              <Link to="/register" className="btn-primary text-xs py-1.5 px-4">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
