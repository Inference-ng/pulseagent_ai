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
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl leading-none">{persona.avatar ?? '🧑🏾'}</span>
          <div>
            <h2 className="text-lg font-bold text-ink">{persona.name ?? persona.user_id}</h2>
            <p className="text-xs text-mist">{persona.description}</p>
          </div>
        </div>
        <span className={sensitivityColor[persona.price_sensitivity]}>
          {sensitivityLabel[persona.price_sensitivity]}
        </span>
      </div>

      <div className="divider my-4" />

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card-sm text-center">
          <p className="eyebrow mb-1">Avg Rating</p>
          <p className="text-xl font-bold text-ink">
            {persona.avg_rating_given !== null ? persona.avg_rating_given.toFixed(1) : '—'}
          </p>
          <p className="text-[10px] text-mist">/ 5.0</p>
        </div>
        <div className="card-sm text-center">
          <p className="eyebrow mb-1">Purchases</p>
          <p className="text-xl font-bold text-ink">{persona.purchase_history.length}</p>
          <p className="text-[10px] text-mist">items</p>
        </div>
        <div className="card-sm text-center">
          <p className="eyebrow mb-1">Mode</p>
          <p className="text-sm font-bold text-ink">{persona.is_cold_start ? 'Cold' : 'Warm'}</p>
          <p className="text-[10px] text-mist">start</p>
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {/* Purchase history */}
        <div className="card-sm">
          <p className="eyebrow mb-2 flex items-center gap-1">
            <ShoppingBag className="h-3 w-3" />History
          </p>
          <div className="flex flex-wrap gap-1.5">
            {persona.purchase_history.length > 0
              ? persona.purchase_history.map((item) => (
                  <span key={item} className="badge-mist truncate max-w-[120px]" title={item}>{item}</span>
                ))
              : <span className="text-xs text-mist italic">No history — cold start</span>
            }
          </div>
        </div>

        {/* Preferred categories */}
        <div className="card-sm">
          <p className="eyebrow mb-2 flex items-center gap-1">
            <Tag className="h-3 w-3" />Categories
          </p>
          <div className="flex flex-wrap gap-1.5">
            {persona.preferred_categories.length > 0
              ? persona.preferred_categories.map((cat) => (
                  <span key={cat} className="badge-emerald capitalize">{cat}</span>
                ))
              : <span className="text-xs text-mist italic">None captured yet</span>
            }
          </div>
        </div>
      </div>

      {persona.context && (
        <p className="mt-4 rounded-xl border border-white/[0.06] bg-surface/50 px-4 py-3 text-xs leading-relaxed text-mist italic">
          "{persona.context}"
        </p>
      )}
    </div>
  );
}
