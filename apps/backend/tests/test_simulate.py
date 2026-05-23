"""Simulate Review Tests — Phase 7"""

import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
@patch("app.routers.simulate.run_task_a", new_callable=AsyncMock)
async def test_simulate_review_endpoint(mock_run_task_a, client):
    """Test that simulate-review endpoint validates payload and returns correct response"""
    mock_run_task_a.return_value = {
        "predicted_rating": 4.5,
        "simulated_review": "Great product!",
        "confidence": 0.9,
        "reasoning": "User likes this."
    }
    response = await client.post(
        "/api/v1/simulate-review",
        json={
            "user_persona": {"user_id": "test_01", "preferred_categories": [], "purchase_history": []},
            "product": {"name": "Test Product", "category": "Tests", "price": 100, "brand": "TestBrand"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_rating" in data
    assert data["predicted_rating"] == 4.5
