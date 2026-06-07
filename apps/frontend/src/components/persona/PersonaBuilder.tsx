import { useForm } from 'react-hook-form';
import { PlusCircle, X } from 'lucide-react';
import type { PriceSensitivity, UserPersona } from '../../types';

interface FormValues {
  name: string;
  description: string;
  avatar: string;
  purchaseHistoryText: string;
  preferredCategoriesText: string;
  avgRatingGiven: string;
  priceSensitivity: PriceSensitivity;
  isColdStart: boolean;
  context: string;
}

function toList(v: string) {
  return v.split(',').map((s) => s.trim()).filter(Boolean);
}
function toId(name: string) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '') || `custom_${Date.now()}`;
}

interface PersonaBuilderProps {
  onSave: (p: UserPersona) => void;
  onClose: () => void;
}

export function PersonaBuilder({ onSave, onClose }: PersonaBuilderProps) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({
    defaultValues: {
      name: '', description: '', avatar: '🧑🏾',
      purchaseHistoryText: '', preferredCategoriesText: '',
      avgRatingGiven: '', priceSensitivity: 'medium',
      isColdStart: false, context: '',
    },
  });

  const onSubmit = handleSubmit((v) => {
    const persona: UserPersona = {
      user_id:              toId(v.name),
      name:                 v.name,
      description:          v.description || 'Custom persona',
      avatar:               v.avatar || '🧑🏾',
      purchase_history:     toList(v.purchaseHistoryText),
      avg_rating_given:     v.avgRatingGiven ? Number(v.avgRatingGiven) : null,
      price_sensitivity:    v.priceSensitivity,
      preferred_categories: toList(v.preferredCategoriesText),
      is_cold_start:        v.isColdStart,
      context:              v.context || undefined,
    };
    onSave(persona);
    reset();
    onClose();
  });

  return (
    <div className="card animate-in">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="eyebrow">Persona builder</p>
          <h2 className="mt-1 text-lg font-bold text-ink">Create a custom profile</h2>
        </div>
        <button type="button" onClick={onClose} className="btn-ghost btn-sm p-2">
          <X className="h-4 w-4" />
        </button>
      </div>

      <form className="grid gap-4 sm:grid-cols-2" onSubmit={onSubmit}>
        <label className="field-label">
          Name *
          <input
            className={`field-input ${errors.name ? 'border-danger/50' : ''}`}
            placeholder="Aisha (Ibadan)"
            {...register('name', { required: 'Name is required' })}
          />
          {errors.name && <span className="text-xs text-danger">{errors.name.message}</span>}
        </label>

        <label className="field-label">
          Avatar Emoji
          <input className="field-input" placeholder="🧑🏾" {...register('avatar')} />
        </label>

        <label className="field-label sm:col-span-2">
          Description
          <input className="field-input" placeholder="Budget-conscious electronics enthusiast from Lagos" {...register('description')} />
        </label>

        <label className="field-label sm:col-span-2">
          Purchase history <span className="normal-case font-normal text-dim">(comma-separated)</span>
          <input className="field-input" placeholder="Oraimo Power Bank, Anker Cable, Samsung A54" {...register('purchaseHistoryText')} />
        </label>

        <label className="field-label sm:col-span-2">
          Preferred categories <span className="normal-case font-normal text-dim">(comma-separated)</span>
          <input className="field-input" placeholder="electronics, accessories, mobile" {...register('preferredCategoriesText')} />
        </label>

        <label className="field-label">
          Avg rating given <span className="normal-case font-normal text-dim">(1–5)</span>
          <input
            className="field-input"
            type="number"
            min="1" max="5" step="0.1"
            placeholder="4.1"
            {...register('avgRatingGiven')}
          />
        </label>

        <label className="field-label">
          Price sensitivity
          <select className="field-input" {...register('priceSensitivity')}>
            <option value="low">Low — premium buyer</option>
            <option value="medium">Medium — balanced</option>
            <option value="high">High — budget-conscious</option>
          </select>
        </label>

        <label className="field-label sm:col-span-2">
          Shopping context
          <textarea
            className="field-input min-h-20 resize-none"
            placeholder="Prefers durable items, shops on Jumia, wary of delivery delays…"
            {...register('context')}
          />
        </label>

        <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-white/[0.08] bg-surface/50 px-4 py-3 text-sm text-mist sm:col-span-2 hover:border-white/[0.14]">
          <input type="checkbox" className="h-4 w-4 rounded accent-emerald" {...register('isColdStart')} />
          Mark as new user with no purchase history (cold-start mode)
        </label>

        <div className="flex gap-3 sm:col-span-2">
          <button type="button" onClick={onClose} className="btn-ghost flex-1">Cancel</button>
          <button type="submit" className="btn-primary flex-1">
            <PlusCircle className="h-4 w-4" />
            Save persona
          </button>
        </div>
      </form>
    </div>
  );
}
