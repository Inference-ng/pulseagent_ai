import { useState } from 'react';
import { motion } from 'framer-motion';
import { ReviewResult } from '../components/results/ReviewResult';
import { RecommendationList } from '../components/results/RecommendationList';
import { TaskAPanel, type TaskAFormValues } from '../components/tasks/TaskAPanel';
import { TaskBPanel, type TaskBFormValues } from '../components/tasks/TaskBPanel';
import { useRecommendations } from '../hooks/useRecommendations';
import { useSimulateReview } from '../hooks/useSimulateReview';

function inferDomain(text: string) {
  const query = text.toLowerCase();

  if (/(food|restaurant|eat|meal|snack|drink)/.test(query)) {
    return 'food' as const;
  }

  if (/(book|read|course|learn|study)/.test(query)) {
    return 'books' as const;
  }

  if (/(phone|laptop|earbud|tv|device|electronics)/.test(query)) {
    return 'electronics' as const;
  }

  return 'fashion' as const;
}

export function DemoPage() {
  const [lastTaskBInput, setLastTaskBInput] = useState<TaskBFormValues>({
    userId: 'tunde_03',
    personaDescription: 'Lagos foodie, loves local restaurants',
  });
  const [followUp, setFollowUp] = useState('');
  const [isFollowUpLoading, setIsFollowUpLoading] = useState(false);

  const review = useSimulateReview();
  const recommendations = useRecommendations();

  const handleTaskASubmit = async (values: TaskAFormValues) => {
    await review.submit({
      user_persona: {
        user_id: values.userId,
        purchase_history: [],
        avg_rating_given: null,
        price_sensitivity: 'medium',
        preferred_categories: [],
        is_cold_start: true,
      },
      product: {
        name: values.itemName,
        category: 'fashion',
        price: 50000,
      },
    });
  };

  const handleTaskBSubmit = async (values: TaskBFormValues) => {
    setLastTaskBInput(values);

    const normalizedUserId = values.userId.trim() || `persona_${Date.now()}`;
    const normalizedPersona = values.personaDescription.trim();

    await recommendations.submit({
      user_persona: {
        user_id: normalizedUserId,
        name: normalizedUserId,
        purchase_history: [],
        avg_rating_given: null,
        price_sensitivity: 'medium',
        preferred_categories: [],
        is_cold_start: true,
        context: normalizedPersona,
      },
      top_k: 10,
      domain: inferDomain(normalizedPersona),
      context_query: normalizedPersona || 'Recommend items based on this user profile.',
    });
  };

  const handleFollowUp = async () => {
    const followUpText = followUp.trim();

    if (!followUpText) {
      return;
    }

    setIsFollowUpLoading(true);
    try {
      const combinedPersona = [lastTaskBInput.personaDescription.trim(), followUpText].filter(Boolean).join(' ');
      await recommendations.submit({
        user_persona: {
          user_id: lastTaskBInput.userId.trim() || `persona_${Date.now()}`,
          purchase_history: [],
          avg_rating_given: null,
          price_sensitivity: 'medium',
          preferred_categories: [],
          is_cold_start: true,
          context: combinedPersona,
        },
        top_k: 10,
        domain: inferDomain(combinedPersona),
        context_query: combinedPersona,
      });
      setFollowUp('');
    } finally {
      setIsFollowUpLoading(false);
    }
  };

  return (
    <div className="space-y-6 py-8">
      <motion.section
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: 'easeOut' }}
        className="grid gap-6 lg:grid-cols-2"
      >
        <div className="space-y-6">
          <TaskAPanel onSubmit={handleTaskASubmit} isLoading={review.isLoading} error={review.error} />

          {review.data ? (
            <ReviewResult result={review.data} />
          ) : (
            <EmptyState
              title="Review output"
              description="Simulate a review to see a star rating and generated review text with a live typewriter reveal."
            />
          )}
        </div>

        <div className="space-y-6">
          <TaskBPanel onSubmit={handleTaskBSubmit} isLoading={recommendations.isLoading} error={recommendations.error} />

          {recommendations.data ? (
            <>
              <RecommendationList result={recommendations.data} />
              <section className="panel-card">
                <p className="text-xs uppercase tracking-[0.28em] text-mist">Conversation</p>
                <h3 className="mt-2 text-xl font-semibold text-ink">Ask a follow-up</h3>
                <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                  <input
                    className="field-input"
                    placeholder="Ask a follow-up"
                    value={followUp}
                    onChange={(event) => setFollowUp(event.target.value)}
                  />
                  <button
                    type="button"
                    onClick={handleFollowUp}
                    disabled={isFollowUpLoading || !followUp.trim()}
                    className="action-button whitespace-nowrap disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {isFollowUpLoading ? 'Thinking...' : 'Send'}
                  </button>
                </div>
              </section>
            </>
          ) : (
            <EmptyState
              title="Recommendation output"
              description="Get recommendations to see a ranked list of 10 items with scores and one-line explanations."
            />
          )}
        </div>
      </motion.section>
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  description: string;
}

function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <section className="panel-card flex min-h-72 flex-col justify-center">
      <p className="text-xs uppercase tracking-[0.28em] text-mist">Awaiting result</p>
      <h3 className="mt-3 text-2xl font-semibold text-ink">{title}</h3>
      <p className="mt-4 max-w-xl text-sm leading-7 text-mist">{description}</p>
    </section>
  );
}