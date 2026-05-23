import type { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  tone?: 'emerald' | 'amber' | 'danger' | 'neutral';
}

const toneClasses = {
  emerald: 'border-emerald/20 bg-emerald/10 text-emerald',
  amber: 'border-amber/20 bg-amber/10 text-amber',
  danger: 'border-danger/20 bg-danger/10 text-danger',
  neutral: 'border-white/10 bg-white/5 text-mist',
};

export function Badge({ children, tone = 'neutral' }: BadgeProps) {
  return <span className={["inline-flex rounded-full border px-3 py-1 text-xs font-semibold", toneClasses[tone]].join(' ')}>{children}</span>;
}