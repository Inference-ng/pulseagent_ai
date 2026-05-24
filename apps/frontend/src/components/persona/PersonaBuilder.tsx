import { useForm } from 'react-hook-form';
import { PlusCircle } from 'lucide-react';
import type { PriceSensitivity, UserPersona } from '../../types';

interface PersonaBuilderProps {
  onSave: (persona: UserPersona) => void;
}

interface PersonaBuilderFormValues {
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

function toList(value: string) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function toPersonaId(name: string) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '') || `custom_${Date.now()}`;
}

export function PersonaBuilder({ onSave }: PersonaBuilderProps) {
  const { register, handleSubmit, reset } = useForm<PersonaBuilderFormValues>({
    defaultValues: {
      name: '',
      description: '',
      avatar: '🧑🏾',
      purchaseHistoryText: '',
      preferredCategoriesText: '',
      avgRatingGiven: '',
      priceSensitivity: 'medium',
      isColdStart: false,
      context: '',
    },
  });

  const onSubmit = handleSubmit((values) => {
    const persona: UserPersona = {
      user_id: toPersonaId(values.name),
      name: values.name,
      description: values.description,
      avatar: values.avatar,
      purchase_history: toList(values.purchaseHistoryText),
      avg_rating_given: values.avgRatingGiven ? Number(values.avgRatingGiven) : null,
      price_sensitivity: values.priceSensitivity,
      preferred_categories: toList(values.preferredCategoriesText),
      is_cold_start: values.isColdStart,
      context: values.context || undefined,
    };

    onSave(persona);
    reset({
      name: '',
      description: '',
      avatar: '🧑🏾',
      purchaseHistoryText: '',
      preferredCategoriesText: '',
      avgRatingGiven: '',
      priceSensitivity: 'medium',
      isColdStart: false,
      context: '',
    });
  });

  return (
    <section className="panel-card">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-mist">Persona builder</p>
          <h2 className="mt-2 text-xl font-semibold text-ink">Create a custom judge profile</h2>
        </div>
        <PlusCircle className="h-5 w-5 text-emerald" />
      </div>

      <form className="mt-6 grid gap-4 md:grid-cols-2" onSubmit={onSubmit}>
        <label className="field-label md:col-span-1">
          Name
          <input className="field-input" placeholder="Aisha (Ibadan)" {...register('name', { required: true })} />
        </label>
        <label className="field-label md:col-span-1">
          Avatar
          <input className="field-input" placeholder="🧑🏾" {...register('avatar')} />
        </label>
        <label className="field-label md:col-span-2">
          Description
          <input className="field-input" placeholder="Budget-conscious electronics enthusiast" {...register('description')} />
        </label>
        <label className="field-label md:col-span-2">
          Purchase history
          <input className="field-input" placeholder="Oraimo Power Bank, Anker Cable, Samsung A54" {...register('purchaseHistoryText')} />
        </label>
        <label className="field-label md:col-span-2">
          Preferred categories
          <input className="field-input" placeholder="electronics, accessories, mobile" {...register('preferredCategoriesText')} />
        </label>
        <label className="field-label">
          Average rating given
          <input className="field-input" type="number" min="1" max="5" step="0.1" placeholder="4.1" {...register('avgRatingGiven')} />
        </label>
        <label className="field-label">
          Price sensitivity
          <select className="field-input" {...register('priceSensitivity')}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
        <label className="field-label md:col-span-2">
          Shopping context
          <textarea
            className="field-input min-h-28 resize-none"
            placeholder="Prefers durable items with strong after-sales support"
            {...register('context')}
          />
        </label>
        <label className="inline-flex items-center gap-3 rounded-3xl border border-white/10 bg-white/5 px-4 py-4 text-sm text-mist md:col-span-2">
          <input type="checkbox" className="h-4 w-4 accent-amber" {...register('isColdStart')} />
          Mark as new user with limited history
        </label>
        <button type="submit" className="action-button md:col-span-2">
          Save custom persona
        </button>
      </form>
    </section>
  );
}