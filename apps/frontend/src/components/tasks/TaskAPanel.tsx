import { useForm } from 'react-hook-form';
import { WandSparkles } from 'lucide-react';
import { LoadingSpinner } from '../ui/LoadingSpinner';
 
export interface TaskAFormValues {
  userId: string;
  itemName: string;
}

interface TaskAPanelProps {
  onSubmit: (values: TaskAFormValues) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export function TaskAPanel({
  onSubmit,
  isLoading,
  error,
}: TaskAPanelProps) {
  const { register, handleSubmit } = useForm<TaskAFormValues>({
    defaultValues: {
      userId: 'emmanuel_01',
      itemName: 'New Balance 550',
    },
  });

  return (
    <section className="panel-card">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-mist">Task A</p>
          <h2 className="mt-2 text-xl font-semibold text-ink">Review Simulator</h2>
        </div>
        <WandSparkles className="h-5 w-5 text-emerald" />
      </div>

      <form className="mt-6 grid gap-4" onSubmit={handleSubmit(onSubmit)}>
        <label className="field-label">
          User ID
          <input className="field-input" placeholder="emmanuel_01" {...register('userId', { required: true })} />
        </label>
        <label className="field-label">
          Item or Product Name
          <input className="field-input" placeholder="Nike Air Max 90" {...register('itemName', { required: true })} />
        </label>
        <button type="submit" disabled={isLoading} className="action-button disabled:cursor-not-allowed disabled:opacity-70">
          {isLoading ? <LoadingSpinner message="Building user profile..." /> : 'Simulate Review'}
        </button>
        {error ? <p className="text-sm text-danger">{error}</p> : null}
      </form>
    </section>
  );
}