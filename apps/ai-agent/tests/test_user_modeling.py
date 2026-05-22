import pytest
from agents.user_modeling_agent import simulate_review

def test_simulate_review_structure():
    persona = {
        "user_id": "test_1",
        "purchase_history": ["Nike Shoes", "Adidas Socks"],
        "avg_rating_given": 4.5,
        "price_sensitivity": "high",
        "preferred_categories": ["Fashion"],
        "is_cold_start": False
    }
    product = {
        "name": "Puma T-Shirt",
        "category": "Fashion",
        "price": 5000,
        "brand": "Puma",
        "description": "A nice t-shirt"
    }
    
    result = simulate_review(persona, product)
    
    assert "predicted_rating" in result
    assert "simulated_review" in result
    assert "confidence" in result
    assert "reasoning" in result
    
    assert 1 <= result["predicted_rating"] <= 5
    assert len(result["simulated_review"]) > 0
