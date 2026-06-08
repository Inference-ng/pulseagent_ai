import { motion } from 'framer-motion';
import { ScoreBar } from '../ui/ScoreBar';
import { Badge } from '../ui/Badge';
import { MessageSquare, Send } from 'lucide-react';
import { useState } from 'react';
import type { RecommendationResponse, Domain } from '../../types';

interface RecommendationListProps {
  result:       RecommendationResponse;
  selectedDomain: Domain;
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

export function RecommendationList({ result, selectedDomain, onFollowUp, isFollowUpLoading }: RecommendationListProps) {
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
      className="card"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Task B — Result</p>
          <h3 className="mt-1 text-lg font-bold text-ink">
            Top {items.length} recommendations
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {result.is_cold_start && <Badge tone="amber">Cold start</Badge>}
          <Badge tone="mist">{result.total} returned</Badge>
        </div>
      </div>

      <div className="divider my-4" />

      {/* Recommendation items */}
      <div className="space-y-3">
        {items.map((item, idx) => {
          const isCrossDomain = item.category.toLowerCase() !== selectedDomain.toLowerCase();

          return (
            <motion.article
              key={item.item_id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04, duration: 0.3 }}
              className="card-sm"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 min-w-0">
                  {/* Rank badge */}
                  <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-surface text-xs font-bold text-mist border border-white/[0.08]">
                    {idx + 1}
                  </span>
                  <div className="min-w-0">
                    <h4 className="text-sm font-semibold text-ink truncate">{item.item_name}</h4>
                    <div className="mt-1 flex flex-wrap items-center gap-1.5">
                      <span className={`badge ${categoryColors[item.category] === 'emerald' ? 'badge-emerald' : 'badge-amber'} text-[10px] capitalize`}>
                        {item.category}
                      </span>
                      {result.is_cold_start && <Badge tone="amber">[COLD START]</Badge>}
                      {isCrossDomain && <Badge tone="mist">[CROSS-DOMAIN]</Badge>}
                    </div>
                  </div>
                </div>
                <div className="flex-shrink-0 text-right">
                  <p className="text-sm font-bold text-ink">{Math.round(item.score * 100)}%</p>
                  <p className="text-[10px] text-mist">match</p>
                </div>
              </div>
              <ScoreBar score={item.score} />
              <p className="mt-2 text-xs leading-5 text-mist italic">{item.reason}</p>
            </motion.article>
          );
        })}
      </div>

      {/* Follow-up conversation */}
      <div className="mt-5 rounded-xl border border-white/[0.06] bg-surface/40 p-4">
        <p className="eyebrow mb-3 flex items-center gap-1.5">
          <MessageSquare className="h-3 w-3" />
          Multi-turn — ask a follow-up
        </p>
        <div className="flex gap-2">
          <input
            className="field-input flex-1 py-2.5 text-xs"
            placeholder="e.g. Show me options under ₦20,000 instead…"
            value={followUp}
            onChange={(e) => setFollowUp(e.target.value)}
            onKeyDown={handleKey}
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={isFollowUpLoading || !followUp.trim()}
            className="btn-primary btn-sm px-3.5"
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
