import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Quote } from 'lucide-react';
import { StarRating } from '../ui/StarRating';
import { Badge } from '../ui/Badge';
import type { SimulateReviewResponse } from '../../types';

interface ReviewResultProps { result: SimulateReviewResponse; }

function confidenceTone(c: number): 'emerald' | 'amber' | 'danger' {
  if (c > 0.7) return 'emerald';
  if (c >= 0.5) return 'amber';
  return 'danger';
}

export function ReviewResult({ result }: ReviewResultProps) {
  const [typed, setTyped] = useState('');
  const tone = confidenceTone(result.confidence);

  useEffect(() => {
    setTyped('');
    let i = 0;
    const t = setInterval(() => {
      i += 2; // 2 chars per tick for speed
      setTyped(result.simulated_review.slice(0, i));
      if (i >= result.simulated_review.length) clearInterval(t);
    }, 16);
    return () => clearInterval(t);
  }, [result.simulated_review]);

  return (
    <motion.section
      className="card animate-in"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 sm:gap-3">
        <div className="min-w-0">
          <p className="eyebrow">Task A — Result</p>
          <h3 className="mt-1 text-base sm:text-lg font-bold text-ink">Simulated review</h3>
        </div>
        <Badge tone={tone}>{Math.round(result.confidence * 100)}% confident</Badge>
      </div>

      <div className="divider my-3 sm:my-4" />

      {/* Rating */}
      <div className="flex items-center gap-3 sm:gap-4">
        <StarRating rating={result.predicted_rating} size="lg" />
        <div>
          <p className="text-2xl sm:text-3xl font-bold text-ink">{result.predicted_rating.toFixed(1)}</p>
          <p className="text-xs text-mist">/ 5.0 predicted</p>
        </div>
      </div>

      {/* Review text */}
      <div className="relative mt-3 sm:mt-4 rounded-xl border border-amber/15 bg-amber/[0.06] px-3.5 py-3 sm:px-5 sm:py-4">
        <Quote className="absolute left-2.5 sm:left-3 top-3 h-4 w-4 text-amber/40" />
        <p className="text-sm leading-6 sm:leading-7 text-ink pl-4">
          {typed}
          <span className="inline-block h-4 w-0.5 bg-emerald align-middle animate-pulse ml-0.5" />
        </p>
      </div>

      {/* Reasoning accordion */}
      <details className="group mt-3 sm:mt-4 rounded-xl border border-white/[0.06] bg-surface/40">
        <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-3 sm:px-4 py-3">
          <span className="text-xs font-semibold text-mist">Agent reasoning</span>
          <ChevronDown className="h-4 w-4 flex-shrink-0 text-mist transition-transform group-open:rotate-180" />
        </summary>
        <p className="border-t border-white/[0.06] px-3 sm:px-4 py-3 text-xs leading-6 text-mist break-words">{result.reasoning}</p>
      </details>
    </motion.section>
  );
}
