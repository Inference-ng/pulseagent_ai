interface LoadingSpinnerProps { message?: string; }

export function LoadingSpinner({ message }: LoadingSpinnerProps) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <span className="spinner" />
      {message && <span className="text-sm font-medium text-ink">{message}</span>}
    </span>
  );
}
