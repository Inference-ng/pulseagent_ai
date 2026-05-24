interface EmptyStateProps { title: string; description: string; icon?: string; }

export function EmptyState({ title, description, icon = '⬡' }: EmptyStateProps) {
  return (
    <div className="card flex min-h-56 flex-col items-center justify-center gap-3 text-center">
      <span className="text-3xl opacity-20">{icon}</span>
      <p className="eyebrow">Awaiting result</p>
      <h3 className="text-lg font-semibold text-ink">{title}</h3>
      <p className="max-w-xs text-sm leading-relaxed text-mist">{description}</p>
    </div>
  );
}
