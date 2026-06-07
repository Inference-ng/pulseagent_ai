import type { ReactNode } from 'react';

type Tone = 'emerald' | 'amber' | 'danger' | 'mist';

interface BadgeProps { children: ReactNode; tone?: Tone; }

export function Badge({ children, tone = 'mist' }: BadgeProps) {
  const cls: Record<Tone, string> = {
    emerald: 'badge-emerald',
    amber:   'badge-amber',
    danger:  'badge-danger',
    mist:    'badge-mist',
  };
  return <span className={cls[tone]}>{children}</span>;
}
