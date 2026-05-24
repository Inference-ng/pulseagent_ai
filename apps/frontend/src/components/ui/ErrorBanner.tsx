import { AlertTriangle, X } from 'lucide-react';

interface ErrorBannerProps { message: string; onDismiss?: () => void; }

export function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-danger/20 bg-danger/8 px-4 py-3">
      <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-danger" />
      <p className="flex-1 text-sm text-danger">{message}</p>
      {onDismiss && (
        <button type="button" onClick={onDismiss} className="text-danger/60 hover:text-danger">
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
