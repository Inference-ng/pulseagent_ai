import { useEffect, useState } from 'react';
import { checkHealth, RUN_MODE } from '../lib/api';
import type { HealthResponse } from '../types';

type Status = 'checking' | 'online' | 'offline' | 'mock';

export function useApiHealth() {
  const [status, setStatus]     = useState<Status>(RUN_MODE === 'mock' ? 'mock' : 'checking');
  const [health, setHealth]     = useState<HealthResponse | null>(null);

  useEffect(() => {
    if (RUN_MODE === 'mock') return;
    checkHealth()
      .then((h) => { setHealth(h); setStatus('online'); })
      .catch(() => setStatus('offline'));
  }, []);

  return { status, health };
}
