import axios from 'axios';
import type {
  RecommendationItem,
  RecommendationRequest,
  RecommendationResponse,
  SimulateReviewRequest,
  SimulateReviewResponse,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 90000,
  headers: {
    'Content-Type': 'application/json',
  },
});

type RunMode = 'mock' | 'api';

const resolveRunMode = (): RunMode => {
  const raw = String(import.meta.env.VITE_RUN_MODE || '').trim().toLowerCase();

  if (raw === 'mock' || raw === 'simulated' || raw === 'demo') {
    return 'mock';
  }

  return 'api';
};

const RUN_MODE = resolveRunMode();

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const MOCK_CATALOG = [
  { item_id: 'rec_001', item_name: 'Nike Air Zoom Lite', category: 'fashion' },
  { item_id: 'rec_002', item_name: 'Adire Premium Kaftan', category: 'fashion' },
  { item_id: 'rec_003', item_name: 'Oraimo FreePods 4', category: 'electronics' },
  { item_id: 'rec_004', item_name: 'Samsung Galaxy A55', category: 'electronics' },
  { item_id: 'rec_005', item_name: 'Atomic Habits', category: 'books' },
  { item_id: 'rec_006', item_name: 'The Psychology of Money', category: 'books' },
  { item_id: 'rec_007', item_name: 'Suya Spot Combo', category: 'food' },
  { item_id: 'rec_008', item_name: 'Jollof Party Box', category: 'food' },
  { item_id: 'rec_009', item_name: 'Casual Denim Jacket', category: 'fashion' },
  { item_id: 'rec_010', item_name: 'Anker 20W Charger', category: 'electronics' },
  { item_id: 'rec_011', item_name: 'Rich Dad Poor Dad', category: 'books' },
  { item_id: 'rec_012', item_name: 'Local Kitchen Weekly Plan', category: 'food' },
];

const buildMockReview = (payload: SimulateReviewRequest): SimulateReviewResponse => {
  const userId = payload.user_persona.user_id;
  const productName = payload.product.name;
  const historySize = payload.user_persona.purchase_history.length;
  const baseRating = 3 + Math.min(1.8, historySize * 0.25);
  const predictedRating = Number(Math.max(1, Math.min(5, baseRating)).toFixed(1));

  return {
    predicted_rating: predictedRating,
    simulated_review: `${productName} feels like a solid fit for ${userId}. The value-to-quality balance is strong, and I would likely recommend it to a friend with similar taste.`,
    confidence: 0.78,
    reasoning: `Mock mode used historical signal count (${historySize}) and persona context to estimate satisfaction for ${productName}.`,
  };
};

const buildMockRecommendations = (payload: RecommendationRequest): RecommendationResponse => {
  const filtered = MOCK_CATALOG.filter((item) => item.category === payload.domain);
  const pool = filtered.length > 0 ? filtered : MOCK_CATALOG;
  const target = Math.max(1, payload.top_k);

  const recommendations: RecommendationItem[] = Array.from({ length: target }, (_, index) => {
    const item = pool[index % pool.length];
    const score = Number(Math.max(0.55, 0.95 - index * 0.035).toFixed(2));

    return {
      item_id: `${item.item_id}_${index + 1}`,
      item_name: item.item_name,
      category: item.category,
      score,
      reason: `Matched to ${payload.domain} intent and user context: ${payload.context_query || 'general preference profile'}.`,
    };
  });

  return {
    recommendations,
    is_cold_start: payload.user_persona.is_cold_start,
    total: recommendations.length,
  };
};

export const simulateReview = async (payload: SimulateReviewRequest) => {
  if (RUN_MODE === 'mock') {
    await wait(1200);
    return buildMockReview(payload);
  }

  const response = await api.post<SimulateReviewResponse>('/api/v1/simulate-review', payload);
  return response.data;
};

export const getRecommendations = async (payload: RecommendationRequest) => {
  if (RUN_MODE === 'mock') {
    await wait(1400);
    return buildMockRecommendations(payload);
  }

  const response = await api.post<RecommendationResponse>('/api/v1/recommend', payload);
  return response.data;
};

export default api;