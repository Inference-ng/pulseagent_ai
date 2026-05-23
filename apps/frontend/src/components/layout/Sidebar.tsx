import { Flame, Users } from 'lucide-react';
import type { UserPersona } from '../../types';

interface SidebarProps {
  personas: UserPersona[];
  selectedPersonaId: string;
  onSelectPersona: (personaId: string) => void;
}

export function Sidebar({ personas, selectedPersonaId, onSelectPersona }: SidebarProps) {
  return (
    <aside className="panel-card h-full">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-mist">Personas</p>
          <h2 className="mt-2 text-xl font-semibold text-ink">Demo roster</h2>
        </div>
        <span className="rounded-full border border-emerald/20 bg-emerald/10 px-3 py-1 text-xs font-semibold text-emerald">
          {personas.length} loaded
        </span>
      </div>

      <div className="mt-6 space-y-3">
        {personas.map((persona) => {
          const isSelected = persona.user_id === selectedPersonaId;

          return (
            <button
              key={persona.user_id}
              type="button"
              onClick={() => onSelectPersona(persona.user_id)}
              className={[
                'w-full rounded-3xl border px-4 py-4 text-left transition',
                isSelected
                  ? 'border-emerald/40 bg-emerald/12 shadow-glow'
                  : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/8',
              ].join(' ')}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-2xl">{persona.avatar ?? '🧑🏾'}</p>
                  <p className="mt-3 text-sm font-semibold text-ink">{persona.name ?? persona.user_id}</p>
                  <p className="mt-1 text-sm text-mist">{persona.description ?? 'Custom persona'}</p>
                </div>
                {persona.is_cold_start ? (
                  <span className="inline-flex items-center gap-1 rounded-full border border-amber/30 bg-amber/10 px-2 py-1 text-[0.7rem] font-semibold uppercase tracking-[0.18em] text-amber">
                    <Flame className="h-3.5 w-3.5" />
                    Cold start
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[0.7rem] font-semibold uppercase tracking-[0.18em] text-mist">
                    <Users className="h-3.5 w-3.5" />
                    Warm profile
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}