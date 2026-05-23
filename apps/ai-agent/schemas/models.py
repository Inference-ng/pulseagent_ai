from pydantic import BaseModel
from typing import List, Optional, Literal

class UserPersona(BaseModel):
    user_id: str
    purchase_history: List[str]
    avg_rating_given: Optional[float] = None
    price_sensitivity: Literal["high", "medium", "low"]
    preferred_categories: List[str]
    is_cold_start: bool = False

class Product(BaseModel):
    name: str
    category: str
    price: float
    brand: str
    description: str = ""


class RecommendationItem(BaseModel):
    item_id: str
    item_name: str
    category: str
    score: float
    reason: str

class RecommendationResult(BaseModel):
    recommendations: List[RecommendationItem]
    is_cold_start: bool
    total: int
