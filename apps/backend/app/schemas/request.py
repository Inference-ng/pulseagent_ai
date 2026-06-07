"""Request Schemas — Pydantic Models for Phase 4"""

from pydantic import BaseModel, Field
from typing import List, Optional


class UserPersonaRequest(BaseModel):
    """User Persona data from frontend"""
    user_id: str
    name: Optional[str] = None
    purchase_history: List[str] = []
    avg_rating_given: Optional[float] = None
    price_sensitivity: Optional[str] = "medium"  # high, medium, low
    preferred_categories: List[str] = []
    is_cold_start: bool = False
    context: Optional[str] = None


class ProductRequest(BaseModel):
    """Product data from frontend"""
    name: str
    category: str
    price: float
    brand: Optional[str] = None
    description: Optional[str] = None


class SimulateReviewRequest(BaseModel):
    """Request for Task A: Simulate Review"""
    user_persona: UserPersonaRequest = Field(..., description="User persona data")
    product: ProductRequest = Field(..., description="Product data")


class RecommendRequest(BaseModel):
    """Request for Task B: Get Recommendations"""
    user_persona: UserPersonaRequest = Field(..., description="User persona data")
    top_k: int = Field(10, ge=1, le=50, description="Number of recommendations")
    domain: str = Field("fashion", description="Product domain")
    context_query: Optional[str] = Field("", description="Conversational query for recommendations")
