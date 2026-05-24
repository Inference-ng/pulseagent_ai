import { ChevronDown } from 'lucide-react';

interface ReasoningCardProps {
  reasoning: string;
}

export function ReasoningCard({ reasoning }: ReasoningCardProps) {
  return (
    <details className="group rounded-3xl border border-white/10 bg-white/5 p-5">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-semibold text-ink">
        Agent reasoning
        <ChevronDown className="h-4 w-4 transition group-open:rotate-180" />
      </summary>
      <p className="mt-4 text-sm leading-7 text-mist">{reasoning}</p>
    </details>
  );
}