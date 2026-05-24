interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message = 'Thinking through the response...' }: LoadingSpinnerProps) {
  return (
    <span className="inline-flex items-center gap-3 text-sm font-medium text-ink">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-emerald/30 border-t-emerald" />
      {message}
    </span>
  );
}