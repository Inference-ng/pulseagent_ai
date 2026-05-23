import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Badge } from '../ui/Badge';
import { StarRating } from '../ui/StarRating';
import { ReasoningCard } from './ReasoningCard';
import type { SimulateReviewResponse } from '../../types';

interface ReviewResultProps {
  result: SimulateReviewResponse;
}

export function ReviewResult({ result }: ReviewResultProps) {
  const tone = result.confidence > 0.7 ? 'emerald' : result.confidence >= 0.5 ? 'amber' : 'danger';
  const [typedReview, setTypedReview] = useState('');

  useEffect(() => {
    setTypedReview('');
    let index = 0;

    const timer = window.setInterval(() => {
      index += 1;
      setTypedReview(result.simulated_review.slice(0, index));

      if (index >= result.simulated_review.length) {
        window.clearInterval(timer);
      }
    }, 14);

    return () => window.clearInterval(timer);
  }, [result.simulated_review]);

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="panel-card"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-mist">Task A result</p>
          <h3 className="mt-2 text-2xl font-semibold text-ink">Simulated review output</h3>
        </div>
        <Badge tone={tone}>{Math.round(result.confidence * 100)}% confident</Badge>
      </div>

      <div className="mt-6 flex items-center gap-4">
        <StarRating rating={result.predicted_rating} />
        <p className="text-3xl font-semibold text-ink">{result.predicted_rating.toFixed(1)}</p>
      </div>

      <blockquote className="mt-6 rounded-[2rem] border border-amber/20 bg-amber/10 px-6 py-5 text-base leading-8 text-ink">
        “{typedReview}”
      </blockquote>

      <div className="mt-6">
        <ReasoningCard reasoning={result.reasoning} />
      </div>
    </motion.section>
  );
}