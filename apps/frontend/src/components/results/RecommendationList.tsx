import { motion } from 'framer-motion';
import { ScoreBar } from '../ui/ScoreBar';
import { Badge } from '../ui/Badge';
import { MessageSquare, Send } from 'lucide-react';
import { useState } from 'react';
import type { RecommendationResponse } from '../../types';

interface RecommendationListProps {
  result:       RecommendationResponse;
  onFollowUp:   (q: string) => Promise<void>;
  isFollowUpLoading: boolean;
}

const categoryColors: Record<string, 'emerald' | 'amber' | 'mist'> = {
  fashion:     'emerald',
  electronics: 'amber',
  books:       'emerald',
  food:        'amber',
  beauty:      'emerald',
  restaurants: 'amber',
};

export function RecommendationList({ result, onFollowUp, isFollowUpLoading }: RecommendationListProps) {
  const [followUp, setFollowUp] = useState('');

  const handleSend = async () => {
    const q = followUp.trim();
    if (!q) return;
    await onFollowUp(q);
    setFollowUp('');
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const items = result.recommendations.slice(0, 10);

  return (
    <motion.section
      className="card overflow-hidden"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 sm:gap-3">
        <div className="min-w-0">
          <p className="eyebrow">Task B — Result</p>
          <h3 className="mt-1 text-base sm:text-lg font-bold text-ink">
            Top {items.length} recommendations
          </h3>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
          {result.is_cold_start && <Badge tone="amber">Cold start</Badge>}
          <Badge tone="mist">{result.total} returned</Badge>
        </div>
      </div>

      <div className="divider my-4" />

      {/* Recommendation items */}
      <div className="space-y-2 sm:space-y-3">
        {items.map((item, idx) => (
          <motion.article
            key={item.item_id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.04, duration: 0.3 }}
            className="card-sm overflow-hidden"
          >
            <div className="flex items-start justify-between gap-2 sm:gap-3">
              <div className="flex items-start gap-2 sm:gap-3 min-w-0 flex-1">
                {/* Rank badge */}
                <span className="flex h-6 w-6 sm:h-7 sm:w-7 flex-shrink-0 items-center justify-center rounded-lg bg-surface text-[10px] sm:text-xs font-bold text-mist border border-white/[0.08]">
                  {idx + 1}
                </span>
                <div className="min-w-0 flex-1 overflow-hidden">
                  <h4 className="text-xs sm:text-sm font-semibold text-ink truncate">{item.item_name}</h4>
                  <span className={`badge ${categoryColors[item.category] === 'emerald' ? 'badge-emerald' : 'badge-amber'} mt-1 text-[10px] capitalize`}>
                    {item.category}
                  </span>
                </div>
              </div>
              <div className="flex-shrink-0 text-right">
                <p className="text-xs sm:text-sm font-bold text-ink">{Math.round(item.score * 100)}%</p>
                <p className="text-[10px] text-mist">match</p>
              </div>
            </div>
            <ScoreBar score={item.score} />
            <p className="mt-1.5 sm:mt-2 text-[11px] sm:text-xs leading-5 text-mist italic break-words">{item.reason}</p>
          </motion.article>
        ))}
      </div>

      {/* Follow-up conversation */}
      <div className="mt-4 sm:mt-5 rounded-xl border border-white/[0.06] bg-surface/40 p-3 sm:p-4">
        <p className="eyebrow mb-2 sm:mb-3 flex items-center gap-1.5">
          <MessageSquare className="h-3 w-3" />
          Multi-turn — ask a follow-up
        </p>
        <div className="flex gap-2 w-full">
          <input
            className="field-input flex-1 min-w-0 py-2 sm:py-2.5 text-xs"
            placeholder="e.g. Options under ₦20k…"
            value={followUp}
            onChange={(e) => setFollowUp(e.target.value)}
            onKeyDown={handleKey}
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={isFollowUpLoading || !followUp.trim()}
            className="btn-primary btn-sm px-3 sm:px-3.5 flex-shrink-0"
          >
            {isFollowUpLoading
              ? <span className="spinner h-3.5 w-3.5" />
              : <Send className="h-3.5 w-3.5" />
            }
          </button>
        </div>
      </div>
    </motion.section>
  );
}
