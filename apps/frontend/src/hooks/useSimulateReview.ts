import { useState } from 'react';
import { simulateReview } from '../lib/api';
import type { SimulateReviewRequest, SimulateReviewResponse } from '../types';

export function useSimulateReview() {
  const [data, setData] = useState<SimulateReviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const submit = async (payload: SimulateReviewRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await simulateReview(payload);
      setData(response);
      return response;
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : 'Unable to simulate review';
      setError(message);
      throw caughtError;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    data,
    error,
    isLoading,
    submit,
  };
}