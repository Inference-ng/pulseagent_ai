import { ChevronDown, UserPlus } from 'lucide-react';
import type { UserPersona } from '../../types';

interface PersonaSelectorProps {
  personas: UserPersona[];
  selectedPersonaId: string;
  onSelectPersona: (personaId: string) => void;
  onBuildCustomPersona: () => void;
}

export function PersonaSelector({
  personas,
  selectedPersonaId,
  onSelectPersona,
  onBuildCustomPersona,
}: PersonaSelectorProps) {
  return (
    <section className="panel-card">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-mist">Persona selector</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Choose a Nigerian demo user or build your own</h2>
        </div>

        <button type="button" onClick={onBuildCustomPersona} className="ghost-button w-full lg:w-auto">
          <UserPlus className="h-4 w-4" />
          Build custom persona
        </button>
      </div>

      <div className="relative mt-5">
        <select
          className="field-input appearance-none pr-12"
          value={selectedPersonaId}
          onChange={(event) => onSelectPersona(event.target.value)}
        >
          {personas.map((persona) => (
            <option key={persona.user_id} value={persona.user_id}>
              {persona.name ?? persona.user_id}
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 text-mist" />
      </div>
    </section>
  );
}