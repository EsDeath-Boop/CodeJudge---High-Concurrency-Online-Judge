import { Link } from 'react-router-dom'
import { Terminal, Zap, Shield, Trophy, ChevronRight } from 'lucide-react'

const features = [
  { icon: Zap,      title: 'Real-time Execution',  desc: 'Submissions judged instantly via async Docker sandboxes. Watch your verdict update live.' },
  { icon: Shield,   title: 'Secure Sandboxing',     desc: 'Every submission isolated — no network, memory-capped, time-limited. Total safety.' },
  { icon: Trophy,   title: 'Competitive Rankings',  desc: 'Per-problem speed rankings. Global leaderboard scored by difficulty.' },
  { icon: Terminal, title: 'Multi-language',        desc: 'C++, Python, Java. Monaco editor with syntax highlighting and IntelliSense.' },
]

export default function Home() {
  return (
    <div className="min-h-screen">

      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center text-center px-4 pt-28 pb-20 overflow-hidden">
        {/* Grid background */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,136,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,136,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
        <div className="absolute inset-0 bg-radial-gradient" style={{background:'radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,255,136,0.06) 0%, transparent 70%)'}} />

        <div className="relative animate-fade-in">
          <div className="inline-flex items-center gap-2 border border-judge-accent/30 bg-judge-accent/5 rounded-full px-4 py-1.5 mb-6 text-judge-accent text-xs font-display">
            <span className="w-1.5 h-1.5 rounded-full bg-judge-accent animate-pulse-slow" />
            ONLINE JUDGE SYSTEM — v2.0
          </div>

          <h1 className="font-display text-5xl md:text-7xl font-bold text-judge-text mb-4 leading-none tracking-tight">
            CODE.<br />
            <span className="text-judge-accent animate-glow">JUDGE.</span><br />
            REPEAT.
          </h1>

          <p className="text-judge-subtext max-w-md mx-auto mb-10 text-lg leading-relaxed">
            Competitive programming judge. Submit code in C++, Python or Java.
            Get verdicts in real-time. Climb the leaderboard.
          </p>

          <div className="flex items-center justify-center gap-4">
            <Link to="/problems" className="btn-primary flex items-center gap-2">
              Start Solving <ChevronRight size={14} />
            </Link>
            <Link to="/leaderboard" className="btn-ghost flex items-center gap-2">
              Leaderboard <Trophy size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-4 pb-24 grid grid-cols-1 md:grid-cols-2 gap-4">
        {features.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="card p-6 hover:border-judge-accent/30 transition-colors duration-300 group">
            <div className="flex items-start gap-4">
              <div className="p-2 rounded bg-judge-accent/10 border border-judge-accent/20 group-hover:border-judge-accent/50 transition-colors">
                <Icon size={16} className="text-judge-accent" />
              </div>
              <div>
                <h3 className="font-display text-judge-text text-sm font-bold mb-1">{title}</h3>
                <p className="text-judge-subtext text-sm leading-relaxed">{desc}</p>
              </div>
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}
