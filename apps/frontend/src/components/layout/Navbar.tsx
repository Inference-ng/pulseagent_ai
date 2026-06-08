import { NavLink } from 'react-router-dom';
import { Github } from 'lucide-react';
import { useApiHealth } from '../../hooks/useApiHealth';

const GITHUB_URL = 'https://github.com/Inference-ng/pulseagent_ai';

export function Navbar() {
  const { status } = useApiHealth();

  const statusLabel: Record<string, string> = {
    checking: 'Connecting…',
    online:   'API Online',
    offline:  'API Offline',
    mock:     'Mock Mode',
  };
  const statusColor: Record<string, string> = {
    checking: 'text-amber animate-pulse',
    online:   'text-emerald',
    offline:  'text-danger',
    mock:     'text-amber',
  };
  const dotColor: Record<string, string> = {
    checking: 'bg-amber animate-pulse',
    online:   'bg-emerald animate-pulse-dot',
    offline:  'bg-danger',
    mock:     'bg-amber',
  };

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-canvas/90 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center gap-3 px-4 py-3 sm:gap-4 sm:px-6 lg:px-8">

        {/* Logo */}
        <NavLink to="/" className="flex flex-shrink-0 items-center gap-2">
          <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-emerald/10 border border-emerald/20 sm:h-8 sm:w-8">
            <span className="h-2 w-2 rounded-full bg-emerald shadow-[0_0_8px_rgba(0,200,150,0.8)] sm:h-2.5 sm:w-2.5" />
          </span>
          <div className="min-w-0">
            <p className="whitespace-nowrap text-sm font-bold tracking-tight text-ink">PulseAgent AI</p>
            <p className="hidden text-[10px] text-mist sm:block">BCT Hackathon 2026</p>
          </div>
        </NavLink>

        {/* Nav links — centered, takes remaining space */}
        <nav className="flex flex-1 items-center justify-center gap-1">
          {[{ to: '/', label: 'Home' }, { to: '/demo', label: 'Demo' }].map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `rounded-lg px-3 py-1.5 text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-emerald/10 text-emerald'
                    : 'text-mist hover:bg-white/[0.05] hover:text-ink'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Right side */}
        <div className="flex flex-shrink-0 items-center gap-2 sm:gap-3">
          {/* API status — dot only on mobile, full label on sm+ */}
          <span className={`flex items-center gap-1.5 text-xs font-medium ${statusColor[status]}`}>
            <span className={`h-1.5 w-1.5 flex-shrink-0 rounded-full ${dotColor[status]}`} />
            <span className="hidden sm:inline">{statusLabel[status]}</span>
          </span>

          {/* GitHub — desktop only */}
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            className="btn-ghost btn-sm hidden items-center gap-1.5 sm:inline-flex"
          >
            <Github className="h-3.5 w-3.5" />
            <span>GitHub</span>
          </a>
        </div>

      </div>
    </header>
  );
}
