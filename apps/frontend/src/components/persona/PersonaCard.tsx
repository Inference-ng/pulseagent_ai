import { ShoppingBag, Star } from 'lucide-react';
import type { UserPersona } from '../../types';

interface PersonaCardProps {
  persona: UserPersona;
}

export function PersonaCard({ persona }: PersonaCardProps) {
  return (
    <article className="panel-card">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-4xl">{persona.avatar ?? '🧑🏾'}</p>
          <h2 className="mt-4 text-2xl font-semibold text-ink">{persona.name ?? persona.user_id}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-mist">{persona.description ?? 'Custom persona ready for evaluation.'}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.22em] text-mist">Price sensitivity</p>
          <p className="mt-2 text-sm font-semibold capitalize text-ink">{persona.price_sensitivity}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="rounded-3xl border border-white/10 bg-black/10 p-4">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.22em] text-mist">
            <ShoppingBag className="h-4 w-4" />
            Purchase history
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {persona.purchase_history.length > 0 ? (
              persona.purchase_history.map((item) => (
                <span key={item} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-ink">
                  {item}
                </span>
              ))
            ) : (
              <span className="text-sm text-mist">No purchase history available.</span>
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-black/10 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-mist">Preferred categories</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {persona.preferred_categories.length > 0 ? (
              persona.preferred_categories.map((category) => (
                <span key={category} className="rounded-full border border-emerald/20 bg-emerald/10 px-3 py-1 text-xs font-medium capitalize text-emerald">
                  {category}
                </span>
              ))
            ) : (
              <span className="text-sm text-mist">No category preferences captured.</span>
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-black/10 p-4">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.22em] text-mist">
            <Star className="h-4 w-4" />
            Average rating given
          </p>
          <p className="mt-3 text-3xl font-semibold text-ink">
            {persona.avg_rating_given !== null ? persona.avg_rating_given.toFixed(1) : 'N/A'}
          </p>
          <p className="mt-2 text-sm text-mist">
            {persona.is_cold_start ? 'Cold-start mode is active for this profile.' : 'Existing behavior signals are available.'}
          </p>
        </div>
      </div>
    </article>
  );
}