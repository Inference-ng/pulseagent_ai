import axios, { AxiosError } from 'axios';
import type {
  HealthResponse,
  RecommendationRequest,
  RecommendationResponse,
  SimulateReviewRequest,
  SimulateReviewResponse,
} from '../types';

// ── Axios instance ────────────────────────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 90_000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Run mode (mock vs real API) ───────────────────────────────
type RunMode = 'mock' | 'api';

const resolveRunMode = (): RunMode => {
  const raw = String(import.meta.env.VITE_RUN_MODE || '').trim().toLowerCase();
  return raw === 'mock' || raw === 'simulated' || raw === 'demo' ? 'mock' : 'api';
};

export const RUN_MODE: RunMode = resolveRunMode();

const wait = (ms: number) => new Promise((res) => setTimeout(res, ms));

// ── Error helpers ─────────────────────────────────────────────
export function extractErrorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ');
    if (err.code === 'ECONNABORTED') return 'Request timed out — the AI agent is taking too long.';
    if (!err.response) return 'Cannot reach the backend. Is it running?';
    return `Server error ${err.response.status}`;
  }
  if (err instanceof Error) return err.message;
  return 'An unexpected error occurred.';
}

// ── Mock data ─────────────────────────────────────────────────
const MOCK_CATALOG = [
  { item_id: 'rec_001', item_name: 'Nike Air Zoom Lite 3',        category: 'fashion',     brand: 'Nike'     },
  { item_id: 'rec_002', item_name: 'Adire Premium Ankara Kaftan',  category: 'fashion',     brand: 'Local'    },
  { item_id: 'rec_003', item_name: 'Oraimo FreePods 4',            category: 'electronics', brand: 'Oraimo'   },
  { item_id: 'rec_004', item_name: 'Samsung Galaxy A55',           category: 'electronics', brand: 'Samsung'  },
  { item_id: 'rec_005', item_name: 'Atomic Habits',                category: 'books',       brand: 'Penguin'  },
  { item_id: 'rec_006', item_name: 'The Psychology of Money',      category: 'books',       brand: 'Harriman' },
  { item_id: 'rec_007', item_name: 'Suya Spot Signature Combo',    category: 'food',        brand: 'Local'    },
  { item_id: 'rec_008', item_name: 'Jollof Party Box (5 persons)', category: 'food',        brand: 'Mama Put'  },
  { item_id: 'rec_009', item_name: 'Casual Denim Jacket',          category: 'fashion',     brand: 'H&M'      },
  { item_id: 'rec_010', item_name: 'Anker 65W GaN Charger',        category: 'electronics', brand: 'Anker'    },
  { item_id: 'rec_011', item_name: 'Rich Dad Poor Dad',            category: 'books',       brand: 'Warner'   },
  { item_id: 'rec_012', item_name: 'Skincare Glow Bundle',         category: 'beauty',      brand: 'SheaMoist'},
  { item_id: 'rec_013', item_name: 'Kilishi Premium Pack',         category: 'food',        brand: 'Local'    },
  { item_id: 'rec_014', item_name: 'Tecno Spark 20 Pro',           category: 'electronics', brand: 'Tecno'    },
];

const MOCK_REVIEWS: Record<string, string> = {
  high:   `Honestly ehn, the quality is okay sha but the price? Abeg. I've seen better on Jumia for less. E fit do the work but I no go pay that amount again. 3 stars and I'm being generous.`,
  medium: `This one dey balance o. E no too cheap, e no too expensive. Quality is solid and I go recommend for my guy who been asking. Value for money is there.`,
  low:    `E dey! This thing is top tier, the build quality alone dey show say na quality product. Packaging was clean, delivery was fast. Gave 5 stars and I stand by am.`,
};

const buildMockReview = (payload: SimulateReviewRequest): SimulateReviewResponse => {
  const ps = payload.user_persona.price_sensitivity;
  const ratingMap: Record<string, number> = { high: 3.0, medium: 3.8, low: 4.7 };
  const confMap:   Record<string, number> = { high: 0.81, medium: 0.76, low: 0.88 };
  return {
    predicted_rating:  ratingMap[ps] ?? 3.5,
    simulated_review:  MOCK_REVIEWS[ps] ?? MOCK_REVIEWS.medium,
    confidence:        confMap[ps] ?? 0.78,
    reasoning: `User is ${ps}-price-sensitive with ${payload.user_persona.purchase_history.length} past purchases. ` +
               `Product category (${payload.product.category}) aligns ${ps === 'low' ? 'well' : 'partially'} with preferred categories. ` +
               `Rating anchored to historical average of ${payload.user_persona.avg_rating_given ?? 'N/A'} ± 1.0.`,
  };
};

const buildMockRecommendations = (payload: RecommendationRequest): RecommendationResponse => {
  const pool = MOCK_CATALOG.filter((i) => i.category === payload.domain);
  const items = (pool.length >= 3 ? pool : MOCK_CATALOG).slice(0, payload.top_k);
  return {
    recommendations: items.map((item, idx) => ({
      item_id:   item.item_id,
      item_name: item.item_name,
      category:  item.category,
      score:     parseFloat(Math.max(0.55, 0.95 - idx * 0.04).toFixed(2)),
      reason:    `Matches your interest in ${payload.domain} and fits ` +
                 `${payload.user_persona.price_sensitivity}-price-sensitivity profile. ` +
                 (payload.context_query ? `Context: "${payload.context_query.slice(0, 60)}".` : ''),
    })),
    is_cold_start: payload.user_persona.is_cold_start,
    total: items.length,
  };
};

// ── Public API functions ──────────────────────────────────────
export const checkHealth = async (): Promise<HealthResponse> => {
  const res = await api.get<HealthResponse>('/health');
  return res.data;
};

export const simulateReview = async (payload: SimulateReviewRequest): Promise<SimulateReviewResponse> => {
  if (RUN_MODE === 'mock') { await wait(1600); return buildMockReview(payload); }
  const res = await api.post<SimulateReviewResponse>('/api/v1/simulate-review', payload);
  return res.data;
};

export const getRecommendations = async (payload: RecommendationRequest): Promise<RecommendationResponse> => {
  if (RUN_MODE === 'mock') { await wait(1800); return buildMockRecommendations(payload); }
  const res = await api.post<RecommendationResponse>('/api/v1/recommend', payload);
  return res.data;
};

export default api;
