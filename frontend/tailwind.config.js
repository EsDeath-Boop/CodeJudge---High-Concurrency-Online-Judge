/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Mono"', 'monospace'],
        body: ['"DM Sans"', 'sans-serif'],
        code: ['"Fira Code"', 'monospace'],
      },
      colors: {
        judge: {
          bg:       '#0a0a0f',
          surface:  '#111118',
          border:   '#1e1e2e',
          accent:   '#00ff88',
          accent2:  '#00b4ff',
          warn:     '#ffaa00',
          danger:   '#ff4455',
          muted:    '#4a4a6a',
          text:     '#e0e0f0',
          subtext:  '#8888aa',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in':   'slideIn 0.3s ease-out',
        'fade-in':    'fadeIn 0.4s ease-out',
        'glow':       'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        slideIn:  { from: { transform: 'translateY(10px)', opacity: 0 }, to: { transform: 'translateY(0)', opacity: 1 } },
        fadeIn:   { from: { opacity: 0 }, to: { opacity: 1 } },
        glow:     { from: { textShadow: '0 0 4px #00ff88' }, to: { textShadow: '0 0 16px #00ff88, 0 0 32px #00ff8844' } },
      }
    }
  },
  plugins: []
}
