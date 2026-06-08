import { ShoppingBag, Tag } from 'lucide-react';
import type { UserPersona } from '../../types';

const sensitivityColor: Record<string, string> = {
  high:   'badge-danger',
  medium: 'badge-amber',
  low:    'badge-emerald',
};
const sensitivityLabel: Record<string, string> = {
  high: 'High sensitivity', medium: 'Mid sensitivity', low: 'Low sensitivity',
};

interface PersonaCardProps { persona: UserPersona; }

export function PersonaCard({ persona }: PersonaCardProps) {
  return (
    <div className="card animate-in">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-2 sm:gap-4">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <span className="text-3xl sm:text-4xl leading-none flex-shrink-0">{persona.avatar ?? '🧑🏾'}</span>
          <div className="min-w-0">
            <h2 className="text-base sm:text-lg font-bold text-ink truncate">{persona.name ?? persona.user_id}</h2>
            <p className="text-xs text-mist line-clamp-2">{persona.description}</p>
          </div>
        </div>
        <span className={`flex-shrink-0 ${sensitivityColor[persona.price_sensitivity]}`}>
          {sensitivityLabel[persona.price_sensitivity]}
        </span>
      </div>

      <div className="divider my-4" />

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2 sm:gap-3">
        <div className="card-sm text-center">
          <p className="eyebrow mb-1 text-[8px] sm:text-[10px]">Avg Rating</p>
          <p className="text-lg sm:text-xl font-bold text-ink">
            {persona.avg_rating_given !== null ? persona.avg_rating_given.toFixed(1) : '—'}
          </p>
          <p className="text-[9px] sm:text-[10px] text-mist">/ 5.0</p>
        </div>
        <div className="card-sm text-center">
          <p className="eyebrow mb-1 text-[8px] sm:text-[10px]">Purchases</p>
          <p className="text-lg sm:text-xl font-bold text-ink">{persona.purchase_history.length}</p>
          <p className="text-[9px] sm:text-[10px] text-mist">items</p>
        </div>
        <div className="card-sm text-center">
          <p className="eyebrow mb-1 text-[8px] sm:text-[10px]">Mode</p>
          <p className="text-sm font-bold text-ink">{persona.is_cold_start ? 'Cold' : 'Warm'}</p>
          <p className="text-[9px] sm:text-[10px] text-mist">start</p>
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {/* Purchase history */}
        <div className="card-sm overflow-hidden">
          <p className="eyebrow mb-2 flex items-center gap-1">
            <ShoppingBag className="h-3 w-3" />History
          </p>
          <div className="flex flex-wrap gap-1 sm:gap-1.5 overflow-hidden">
            {persona.purchase_history.length > 0
              ? persona.purchase_history.map((item) => (
                  <span key={item} className="badge-mist truncate max-w-[70px] sm:max-w-[120px] text-[10px] sm:text-xs" title={item}>{item}</span>
                ))
              : <span className="text-xs text-mist italic">No history — cold start</span>
            }
          </div>
        </div>

        {/* Preferred categories */}
        <div className="card-sm overflow-hidden">
          <p className="eyebrow mb-2 flex items-center gap-1">
            <Tag className="h-3 w-3" />Categories
          </p>
          <div className="flex flex-wrap gap-1 sm:gap-1.5 overflow-hidden">
            {persona.preferred_categories.length > 0
              ? persona.preferred_categories.map((cat) => (
                  <span key={cat} className="badge-emerald capitalize text-[10px] sm:text-xs">{cat}</span>
                ))
              : <span className="text-xs text-mist italic">None captured yet</span>
            }
          </div>
        </div>
      </div>

      {persona.context && (
        <p className="mt-4 rounded-xl border border-white/[0.06] bg-surface/50 px-3 py-3 sm:px-4 text-xs leading-relaxed text-mist italic break-words">
          "{persona.context}"
        </p>
      )}
    </div>
  );
}
