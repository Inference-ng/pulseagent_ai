import { useState } from 'react';
import { getRecommendations, extractErrorMessage } from '../lib/api';
import type { RecommendationRequest, RecommendationResponse } from '../types';

export function useRecommendations() {
  const [data, setData]         = useState<RecommendationResponse | null>(null);
  const [error, setError]       = useState<string | null>(null);
  const [isLoading, setLoading] = useState(false);

  const submit = async (payload: RecommendationRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getRecommendations(payload);
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
