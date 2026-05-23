import { NavLink } from 'react-router-dom';
import { Github } from 'lucide-react';

const links = [
  { to: '/', label: 'Home' },
  { to: '/demo', label: 'Demo' },
];

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-canvas/85 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <NavLink to="/" className="flex items-center gap-3 text-sm font-semibold tracking-[0.18em] text-ink">
          <span className="h-3 w-3 rounded-full bg-emerald shadow-[0_0_18px_rgba(16,185,129,0.9)]" />
          <span>
            PurseAgent AI
            <span className="block text-[0.64rem] font-medium tracking-[0.18em] text-mist">
              Judge-ready frontend dashboard
            </span>
          </span>
        </NavLink>

        <nav className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 p-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                [
                  'rounded-full px-4 py-2 text-sm font-medium transition',
                  isActive ? 'bg-emerald text-canvas' : 'text-mist hover:text-ink',
                ].join(' ')
              }
            >
              {link.label}
            </NavLink>
          ))}
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-2 rounded-full bg-amber px-4 py-2 text-sm font-semibold text-canvas sm:inline-flex"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
}