import { useForm } from 'react-hook-form';
import { Radar } from 'lucide-react';
import { LoadingSpinner } from '../ui/LoadingSpinner';
 
export interface TaskBFormValues {
  userId: string;
  personaDescription: string;
}

interface TaskBPanelProps {
  onSubmit: (values: TaskBFormValues) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export function TaskBPanel({
  onSubmit,
  isLoading,
  error,
}: TaskBPanelProps) {
  const { register, handleSubmit } = useForm<TaskBFormValues>({
    defaultValues: {
      userId: 'tunde_03',
      personaDescription: 'Lagos foodie, loves local restaurants',
    },
  });

  return (
    <section className="panel-card">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-mist">Task B</p>
          <h2 className="mt-2 text-xl font-semibold text-ink">Recommender</h2>
        </div>
        <Radar className="h-5 w-5 text-emerald" />
      </div>

      <form className="mt-6 grid gap-4" onSubmit={handleSubmit(onSubmit)}>
        <label className="field-label">
          User ID (optional)
          <input className="field-input" placeholder="tunde_03" {...register('userId')} />
        </label>
        <label className="field-label">
          Persona description
          <textarea
            className="field-input min-h-28 resize-none"
            placeholder="Lagos foodie, loves local restaurants"
            {...register('personaDescription')}
          />
          <span className="text-xs text-mist">Provide either a User ID or persona description.</span>
        </label>
        <button type="submit" disabled={isLoading} className="action-button disabled:cursor-not-allowed disabled:opacity-70">
          {isLoading ? <LoadingSpinner message="Building user profile..." /> : 'Get Recommendations'}
        </button>
        {error ? <p className="text-sm text-danger">{error}</p> : null}
      </form>
    </section>
  );
}