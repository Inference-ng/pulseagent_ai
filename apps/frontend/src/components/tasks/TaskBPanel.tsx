import { useForm } from 'react-hook-form';
import { Radar } from 'lucide-react';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { ErrorBanner } from '../ui/ErrorBanner';
import type { Domain, UserPersona } from '../../types';

export interface TaskBFormValues {
  domain:       Domain;
  contextQuery: string;
  topK:         number;
}

interface TaskBPanelProps {
  persona:      UserPersona;
  onSubmit:     (v: TaskBFormValues) => Promise<void>;
  isLoading:    boolean;
  error:        string | null;
  onClearError: () => void;
}

const DOMAINS: { value: Domain; label: string }[] = [
  { value: 'fashion',     label: '👗 Fashion'     },
  { value: 'electronics', label: '📱 Electronics' },
  { value: 'books',       label: '📚 Books'       },
  { value: 'food',        label: '🍲 Food'        },
  { value: 'beauty',      label: '✨ Beauty'      },
  { value: 'restaurants', label: '🍽️ Restaurants' },
];

function inferDomain(text: string): Domain {
  const q = text.toLowerCase();
  if (/(food|eat|meal|snack|drink|suya|jollof|restaurant|amala)/.test(q)) return 'food';
  if (/(book|read|course|learn|study|novel)/.test(q)) return 'books';
  if (/(phone|laptop|earbud|tv|device|gadget|charger|tech)/.test(q)) return 'electronics';
  if (/(beauty|skincare|makeup|lipstick|cream|serum)/.test(q)) return 'beauty';
  if (/(restaurant|bar|lounge|eatery|kitchen)/.test(q)) return 'restaurants';
  return 'fashion';
}

export function TaskBPanel({ persona, onSubmit, isLoading, error, onClearError }: TaskBPanelProps) {
  const { register, handleSubmit, watch, setValue } = useForm<TaskBFormValues>({
    defaultValues: {
      domain:       inferDomain(persona.context ?? persona.preferred_categories.join(' ')),
      contextQuery: persona.context ?? '',
      topK:         10,
    },
  });

  const contextQuery = watch('contextQuery');

  // Auto-infer domain from context
  const handleContextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue('contextQuery', e.target.value);
    if (e.target.value.trim().length > 5) {
      setValue('domain', inferDomain(e.target.value));
    }
  };

  return (
    <section className="card">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow mb-1">Task B — Recommendation</p>
          <h2 className="text-lg font-bold text-ink">Recommender</h2>
          <p className="mt-0.5 text-xs text-mist">
            Ranking for <span className="font-semibold text-emerald">{persona.name ?? persona.user_id}</span>
            {persona.is_cold_start && (
              <span className="ml-1.5 badge-amber text-[10px]">cold start</span>
            )}
          </p>
        </div>
        <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-emerald/10 border border-emerald/20">
          <Radar className="h-4 w-4 text-emerald" />
        </span>
      </div>

      <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <label className="field-label sm:col-span-2">
          Context / Shopping intent
          <textarea
            className="field-input min-h-24 resize-none"
            placeholder="e.g. I need an owambe outfit for a Lagos wedding…"
            value={contextQuery}
            {...register('contextQuery')}
            onChange={handleContextChange}
          />
          <span className="normal-case font-normal text-dim text-[11px]">Domain is inferred automatically from your text.</span>
        </label>

        <label className="field-label">
          Domain
          <select className="field-input" {...register('domain')}>
            {DOMAINS.map(({ value, label }) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>

        <label className="field-label">
          Results (top-K)
          <input
            className="field-input"
            type="number"
            min="1" max="20"
            {...register('topK', { valueAsNumber: true })}
          />
        </label>

        {error && (
          <div className="sm:col-span-2">
            <ErrorBanner message={error} onDismiss={onClearError} />
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary sm:col-span-2"
        >
          {isLoading
            ? <LoadingSpinner message="Ranking items…" />
            : <><Radar className="h-4 w-4" />Get Recommendations</>
          }
        </button>
      </form>
    </section>
  );
}
