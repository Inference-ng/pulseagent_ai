import { motion } from 'framer-motion';
import { UserPlus, Flame, Users } from 'lucide-react';
import type { UserPersona } from '../../types';

interface PersonaStripProps {
  personas: UserPersona[];
  selectedId: string;
  onSelect: (id: string) => void;
  onBuildCustom: () => void;
}

export function PersonaStrip({ personas, selectedId, onSelect, onBuildCustom }: PersonaStripProps) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="eyebrow">Step 1 — Choose a persona</p>
          <h2 className="mt-1 text-base font-semibold text-ink">Select a Nigerian demo user to begin</h2>
        </div>
        <button type="button" onClick={onBuildCustom} className="btn-ghost btn-sm hidden items-center gap-1.5 sm:inline-flex">
          <UserPlus className="h-3.5 w-3.5" />
          Custom
        </button>
      </div>

      {/* Scrollable persona row */}
      <div className="flex gap-3 overflow-x-auto pb-1 sm:grid sm:grid-cols-4 sm:overflow-visible">
        {personas.map((p, i) => {
          const isActive = p.user_id === selectedId;
          return (
            <motion.button
              key={p.user_id}
              type="button"
              onClick={() => onSelect(p.user_id)}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06, duration: 0.3 }}
              className={`persona-card flex-shrink-0 w-44 sm:w-auto text-left ${isActive ? 'persona-card-active' : ''}`}
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-2xl leading-none">{p.avatar ?? '🧑🏾'}</span>
                {p.is_cold_start ? (
                  <span className="badge-amber inline-flex items-center gap-0.5 text-[10px]">
                    <Flame className="h-2.5 w-2.5" />Cold
                  </span>
                ) : (
                  <span className="badge-mist inline-flex items-center gap-0.5 text-[10px]">
                    <Users className="h-2.5 w-2.5" />Warm
                  </span>
                )}
              </div>
              <p className="mt-2.5 text-sm font-semibold text-ink">{p.name ?? p.user_id}</p>
              <p className="mt-0.5 text-xs leading-snug text-mist line-clamp-2">{p.description}</p>

              {/* Active indicator */}
              {isActive && (
                <div className="mt-2.5 flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald animate-pulse-dot" />
                  <span className="text-[10px] font-semibold text-emerald">Selected</span>
                </div>
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Mobile custom button */}
      <button type="button" onClick={onBuildCustom} className="btn-ghost btn-sm mt-3 inline-flex w-full items-center justify-center gap-1.5 sm:hidden">
        <UserPlus className="h-3.5 w-3.5" />
        Build custom persona
      </button>
    </section>
  );
}
