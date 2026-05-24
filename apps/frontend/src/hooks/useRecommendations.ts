import { useState } from 'react';
import { getRecommendations } from '../lib/api';
import type { RecommendationRequest, RecommendationResponse } from '../types';

export function useRecommendations() {
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const submit = async (payload: RecommendationRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getRecommendations(payload);
      setData(response);
      return response;
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : 'Unable to fetch recommendations';
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