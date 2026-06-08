import { useForm } from 'react-hook-form';
import { WandSparkles } from 'lucide-react';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { ErrorBanner } from '../ui/ErrorBanner';
import type { UserPersona } from '../../types';

export interface TaskAFormValues {
  itemName:        string;
  itemCategory:    string;
  itemPrice:       number;
  itemBrand:       string;
  itemDescription: string;
}

interface TaskAPanelProps {
  persona:   UserPersona;
  onSubmit:  (v: TaskAFormValues) => Promise<void>;
  isLoading: boolean;
  error:     string | null;
  onClearError: () => void;
}

const CATEGORY_OPTIONS = [
  'fashion', 'electronics', 'books', 'food', 'beauty', 'sportswear',
  'footwear', 'accessories', 'home & living', 'health',
];

export function TaskAPanel({ persona, onSubmit, isLoading, error, onClearError }: TaskAPanelProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<TaskAFormValues>({
    defaultValues: {
      itemName:        'New Balance 550',
      itemCategory:    'footwear',
      itemPrice:       45000,
      itemBrand:       'New Balance',
      itemDescription: 'Lifestyle sneaker with premium leather upper and retro silhouette.',
    },
  });

  return (
    <section className="card">
      <div className="mb-4 sm:mb-5 flex items-start justify-between gap-2 sm:gap-4">
        <div className="min-w-0 flex-1">
          <p className="eyebrow mb-1">Task A — User Modeling</p>
          <h2 className="text-base sm:text-lg font-bold text-ink">Review Simulator</h2>
          <p className="mt-0.5 text-xs text-mist truncate">
            Generating as <span className="font-semibold text-emerald">{persona.name ?? persona.user_id}</span>
          </p>
        </div>
        <span className="flex h-8 w-8 sm:h-9 sm:w-9 flex-shrink-0 items-center justify-center rounded-xl bg-emerald/10 border border-emerald/20">
          <WandSparkles className="h-4 w-4 text-emerald" />
        </span>
      </div>

      <form className="grid gap-3 sm:gap-4 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <label className="field-label sm:col-span-2">
          Product name *
          <input
            className={`field-input ${errors.itemName ? 'border-danger/50' : ''}`}
            placeholder="e.g. Nike Air Max 90"
            {...register('itemName', { required: 'Product name is required' })}
          />
          {errors.itemName && <span className="text-xs text-danger">{errors.itemName.message}</span>}
        </label>

        <label className="field-label">
          Category
          <select className="field-input" {...register('itemCategory')}>
            {CATEGORY_OPTIONS.map((c) => (
              <option key={c} value={c} className="capitalize">{c}</option>
            ))}
          </select>
        </label>

        <label className="field-label">
          Price (₦)
          <input
            className="field-input"
            type="number"
            min="0"
            step="500"
            placeholder="45000"
            {...register('itemPrice', { valueAsNumber: true, min: 0 })}
          />
        </label>

        <label className="field-label">
          Brand
          <input className="field-input" placeholder="Nike, Zara, Oraimo…" {...register('itemBrand')} />
        </label>

        <label className="field-label">
          Description <span className="normal-case font-normal text-dim">(optional)</span>
          <input className="field-input" placeholder="Brief product description" {...register('itemDescription')} />
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
            ? <LoadingSpinner message="Simulating review…" />
            : <><WandSparkles className="h-4 w-4" />Simulate Review</>
          }
        </button>
      </form>
    </section>
  );
}
