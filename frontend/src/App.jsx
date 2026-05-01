import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import Home          from './pages/Home'
import Login         from './pages/Login'
import Register      from './pages/Register'
import Problems      from './pages/Problems'
import ProblemSolver from './pages/ProblemSolver'
import Leaderboard   from './pages/Leaderboard'
import Profile       from './pages/Profile'
import './index.css'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-judge-bg">
          <Navbar />
          <Routes>
            <Route path="/"              element={<Home />} />
            <Route path="/login"         element={<Login />} />
            <Route path="/register"      element={<Register />} />
            <Route path="/problems"      element={<Problems />} />
            <Route path="/problems/:slug" element={<ProblemSolver />} />
            <Route path="/leaderboard"   element={<Leaderboard />} />
            <Route path="/profile"       element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          </Routes>
        </div>
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: '#111118',
              color: '#e0e0f0',
              border: '1px solid #1e1e2e',
              fontFamily: '"DM Sans", sans-serif',
              fontSize: '13px',
            },
            success: { iconTheme: { primary: '#00ff88', secondary: '#0a0a0f' } },
            error:   { iconTheme: { primary: '#ff4455', secondary: '#0a0a0f' } },
          }}
        />
      </BrowserRouter>
    </AuthProvider>
  )
}
