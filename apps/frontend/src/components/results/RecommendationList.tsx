import { motion } from 'framer-motion';
import { Badge } from '../ui/Badge';
import type { RecommendationResponse } from '../../types';

interface RecommendationListProps {
  result: RecommendationResponse;
}

export function RecommendationList({ result }: RecommendationListProps) {
  const rankedItems = result.recommendations.slice(0, 10);

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="panel-card"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-mist">Task B result</p>
          <h3 className="mt-2 text-2xl font-semibold text-ink">Top 10 ranked recommendations</h3>
        </div>
        <Badge>{rankedItems.length} returned</Badge>
      </div>

      <div className="mt-6 space-y-4">
        {rankedItems.map((item, index) => (
          <article key={item.item_id} className="rounded-[2rem] border border-white/10 bg-white/5 p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="inline-flex rounded-full border border-white/10 bg-black/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-mist">
                  #{index + 1}
                </p>
                <h4 className="mt-2 text-lg font-semibold text-ink">{item.item_name}</h4>
                <p className="mt-2 inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium capitalize text-mist">
                  {item.category}
                </p>
              </div>
              <Badge tone="emerald">{Math.round(item.score * 100)} match</Badge>
            </div>

            <div className="mt-4 h-2 rounded-full bg-white/10">
              <div className="h-full rounded-full bg-gradient-to-r from-emerald to-amber" style={{ width: `${Math.max(8, item.score * 100)}%` }} />
            </div>

            <p className="mt-4 text-sm italic leading-7 text-mist">{item.reason}</p>
          </article>
        ))}
      </div>
    </motion.section>
  );
}