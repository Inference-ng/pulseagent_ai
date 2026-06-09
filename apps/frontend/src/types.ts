export type PriceSensitivity = 'low' | 'medium' | 'high';
export type Domain = 'fashion' | 'electronics' | 'books' | 'food' | 'beauty' | 'restaurants';

export interface UserPersona {
  user_id:              string;
  name?:                string;
  avatar?:              string;
  description?:         string;
  purchase_history:     string[];
  avg_rating_given:     number | null;
  price_sensitivity:    PriceSensitivity;
  preferred_categories: string[];
  is_cold_start:        boolean;
  context?:             string;
}

export interface ProductInput {
  name:         string;
  category:     string;
  price:        number;
  brand?:       string;
  description?: string;
}

export interface SimulateReviewRequest {
  user_persona: UserPersona;
  product:      ProductInput;
}

export interface SimulateReviewResponse {
  predicted_rating: number;
  simulated_review: string;
  confidence:       number;
  reasoning:        string;
}

export interface RecommendationItem {
  item_id:   string;
  item_name: string;
  category:  string;
  score:     number;
  reason:    string;
  price?:    number;   // NGN price
  brand?:    string;
}

export interface RecommendationRequest {
  user_persona:  UserPersona;
  top_k:         number;
  domain:        Domain;
  context_query: string;
}

export interface RecommendationResponse {
  recommendations: RecommendationItem[];
  is_cold_start:   boolean;
  total:           number;
}

export interface HealthResponse {
  status:      string;
  version:     string;
  app_name:    string;
  environment: string;
  database:    string;
  tasks:       string[];
}