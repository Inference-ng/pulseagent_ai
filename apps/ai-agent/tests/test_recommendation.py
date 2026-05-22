import pytest
from agents.recommendation_agent import get_recommendations

def test_get_recommendations():
    persona = {
        "user_id": "test_1",
        "purchase_history": ["Nike Shoes", "Adidas Socks"],
        "avg_rating_given": 4.5,
        "price_sensitivity": "high",
        "preferred_categories": ["Fashion"],
        "is_cold_start": False
    }
    
    result = get_recommendations(persona, top_k=5, domain="fashion")
    
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)
    
def test_cold_start_recommendations():
    persona = {
        "user_id": "test_2",
        "purchase_history": [],
        "avg_rating_given": None,
        "price_sensitivity": "medium",
        "preferred_categories": ["Electronics"],
        "is_cold_start": True
    }
    
    result = get_recommendations(persona, top_k=5, domain="electronics", context_query="looking for a phone")
    
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)
