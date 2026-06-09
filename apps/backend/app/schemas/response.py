"""Response Schemas — Pydantic Models"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SimulateReviewResponse(BaseModel):
    """Response for Task A: Simulated Review"""
    predicted_rating: float = Field(..., description="Predicted star rating (1-5)")
    simulated_review: str   = Field(..., description="Generated review text")
    confidence:       float = Field(..., description="Confidence score (0-1)")
    reasoning:        str   = Field(..., description="Explanation of the prediction")


class RecommendationItem(BaseModel):
    """Single recommendation item"""
    item_id:   str
    item_name: str
    category:  str
    score:     float          = Field(..., description="Relevance score (0-1)")
    reason:    str            = Field(..., description="Why this item is recommended")
    price:     Optional[int]  = Field(None, description="Price in NGN (Naira)")
    brand:     Optional[str]  = Field(None, description="Product brand")


class RecommendResponse(BaseModel):
    """Response for Task B: Recommendations"""
    recommendations: List[RecommendationItem]
    is_cold_start:   bool
    total:           int = Field(..., description="Number of recommendations returned")


class HealthResponse(BaseModel):
    """Health check response"""
    status:   str
    version:  str
    database: Optional[str] = None