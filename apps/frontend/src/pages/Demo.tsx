import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { PersonaStrip }         from '../components/persona/PersonaStrip';
import { PersonaCard }          from '../components/persona/PersonaCard';
import { PersonaBuilder }       from '../components/persona/PersonaBuilder';
import { TaskAPanel }           from '../components/tasks/TaskAPanel';
import { TaskBPanel }           from '../components/tasks/TaskBPanel';
import { ReviewResult }         from '../components/results/ReviewResult';
import { RecommendationList }   from '../components/results/RecommendationList';
import { EmptyState }           from '../components/ui/EmptyState';
import { SkeletonResult, SkeletonRecommendations } from '../components/results/SkeletonResult';
import { useSimulateReview }    from '../hooks/useSimulateReview';
import { useRecommendations }   from '../hooks/useRecommendations';
import { DEMO_PERSONAS }        from '../data/demo-personas';
import type { UserPersona, Domain } from '../types';
import type { TaskAFormValues } from '../components/tasks/TaskAPanel';
import type { TaskBFormValues } from '../components/tasks/TaskBPanel';

export function DemoPage() {
  // ── Persona state ─────────────────────────────────────────
  const [personas, setPersonas]         = useState<UserPersona[]>(DEMO_PERSONAS);
  const [selectedId, setSelectedId]     = useState<string>(DEMO_PERSONAS[0].user_id);
  const [showBuilder, setShowBuilder]   = useState(false);

  const selectedPersona = personas.find((p) => p.user_id === selectedId) ?? personas[0];

  const handleSavePersona = useCallback((p: UserPersona) => {
    setPersonas((prev) => {
      const exists = prev.findIndex((x) => x.user_id === p.user_id);
      if (exists >= 0) {
        const next = [...prev]; next[exists] = p; return next;
      }
      return [...prev, p];
    });
    setSelectedId(p.user_id);
  }, []);

  // ── Task A ────────────────────────────────────────────────
  const review = useSimulateReview();

  const handleTaskASubmit = useCallback(async (v: TaskAFormValues) => {
    await review.submit({
      user_persona: {
        user_id:              selectedPersona.user_id,
        purchase_history:     selectedPersona.purchase_history,
        avg_rating_given:     selectedPersona.avg_rating_given,
        price_sensitivity:    selectedPersona.price_sensitivity,
        preferred_categories: selectedPersona.preferred_categories,
        is_cold_start:        selectedPersona.is_cold_start,
        context:              selectedPersona.context,
      },
      product: {
        name:        v.itemName,
        category:    v.itemCategory,
        price:       v.itemPrice,
        brand:       v.itemBrand    || undefined,
        description: v.itemDescription || undefined,
      },
    });
  }, [selectedPersona, review]);

  // ── Task B ────────────────────────────────────────────────
  const recommendations = useRecommendations();
  const [followUpLoading, setFollowUpLoading] = useState(false);
  const [lastBValues, setLastBValues] = useState<TaskBFormValues>({
    domain: 'fashion', contextQuery: '', topK: 10,
  });

  const handleTaskBSubmit = useCallback(async (v: TaskBFormValues) => {
    setLastBValues(v);
    await recommendations.submit({
      user_persona: {
        user_id:              selectedPersona.user_id,
        purchase_history:     selectedPersona.purchase_history,
        avg_rating_given:     selectedPersona.avg_rating_given,
        price_sensitivity:    selectedPersona.price_sensitivity,
        preferred_categories: selectedPersona.preferred_categories,
        is_cold_start:        selectedPersona.is_cold_start,
        context:              selectedPersona.context,
      },
      top_k:         v.topK,
      domain:        v.domain as Domain,
      context_query: v.contextQuery || selectedPersona.context || '',
    });
  }, [selectedPersona, recommendations]);

  const handleFollowUp = useCallback(async (query: string) => {
    setFollowUpLoading(true);
    try {
      const combined = [lastBValues.contextQuery, query].filter(Boolean).join('. ');
      await recommendations.submit({
        user_persona: {
          user_id:              selectedPersona.user_id,
          purchase_history:     selectedPersona.purchase_history,
          avg_rating_given:     selectedPersona.avg_rating_given,
          price_sensitivity:    selectedPersona.price_sensitivity,
          preferred_categories: selectedPersona.preferred_categories,
          is_cold_start:        selectedPersona.is_cold_start,
          context:              selectedPersona.context,
        },
        top_k:         lastBValues.topK,
        domain:        lastBValues.domain as Domain,
        context_query: combined,
      });
    } finally {
      setFollowUpLoading(false);
    }
  }, [selectedPersona, lastBValues, recommendations]);

  // ── When persona changes, clear results ───────────────────
  const handleSelectPersona = (id: string) => {
    setSelectedId(id);
    review.reset();
    recommendations.reset();
  };

  return (
    <div className="space-y-6 py-6 sm:py-8">

      {/* ── Persona strip ── */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <PersonaStrip
          personas={personas}
          selectedId={selectedId}
          onSelect={handleSelectPersona}
          onBuildCustom={() => setShowBuilder((v) => !v)}
        />
      </motion.div>

      {/* ── Custom persona builder ── */}
      {showBuilder && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <PersonaBuilder onSave={handleSavePersona} onClose={() => setShowBuilder(false)} />
        </motion.div>
      )}

      {/* ── Selected persona detail card ── */}
      <PersonaCard persona={selectedPersona} />

      <div className="divider" />

      {/* ── Task panels ── */}
      <div className="grid gap-6 lg:grid-cols-2">

        {/* Task A column */}
        <div className="space-y-5">
          <TaskAPanel
            persona={selectedPersona}
            onSubmit={handleTaskASubmit}
            isLoading={review.isLoading}
            error={review.error}
            onClearError={() => review.reset()}
          />
          {review.isLoading && <SkeletonResult />}
          {!review.isLoading && review.data && <ReviewResult result={review.data} />}
          {!review.isLoading && !review.data && !review.error && (
            <EmptyState
              title="Review output"
              description="Fill in a product above and hit Simulate Review. The agent will generate a rating and authentic Nigerian review text."
              icon="✍️"
            />
          )}
        </div>

        {/* Task B column */}
        <div className="space-y-5">
          <TaskBPanel
            persona={selectedPersona}
            onSubmit={handleTaskBSubmit}
            isLoading={recommendations.isLoading}
            error={recommendations.error}
            onClearError={() => recommendations.reset()}
          />
          {recommendations.isLoading && <SkeletonRecommendations />}
          {!recommendations.isLoading && recommendations.data && (
            <RecommendationList
              result={recommendations.data}
              onFollowUp={handleFollowUp}
              isFollowUpLoading={followUpLoading}
            />
          )}
          {!recommendations.isLoading && !recommendations.data && !recommendations.error && (
            <EmptyState
              title="Recommendation output"
              description="Describe what your user is shopping for and hit Get Recommendations. Results are ranked by FAISS + Gemini re-ranking."
              icon="🎯"
            />
          )}
        </div>
      </div>
    </div>
  );
}
