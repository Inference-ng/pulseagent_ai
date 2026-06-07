import { useState } from 'react';
import { simulateReview, extractErrorMessage } from '../lib/api';
import type { SimulateReviewRequest, SimulateReviewResponse } from '../types';

export function useSimulateReview() {
  const [data, setData]         = useState<SimulateReviewResponse | null>(null);
  const [error, setError]       = useState<string | null>(null);
  const [isLoading, setLoading] = useState(false);

  const submit = async (payload: SimulateReviewRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await simulateReview(payload);
      setData(res);
      return res;
    } catch (err) {
      const msg = extractErrorMessage(err);
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => { setData(null); setError(null); };

  return { data, error, isLoading, submit, reset };
}
