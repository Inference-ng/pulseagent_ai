"""Recommendation Tests — Phase 7"""

import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_recommend_endpoint(client):
    """Test that recommend endpoint validates payload and returns correct response"""
    with patch("app.routers.recommend.run_task_b", new_callable=AsyncMock) as mock_run_task_b:
        mock_run_task_b.return_value = {
            "recommendations": [{"item_id": "1", "item_name": "Test", "category": "fashion", "score": 0.9, "reason": "Test"}],
            "is_cold_start": False,
            "total": 1
        }
        response = await client.post(
            "/api/v1/recommend",
            json={
                "user_persona": {"user_id": "test_01", "preferred_categories": [], "purchase_history": []},
                "top_k": 10,
                "domain": "fashion",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) == 1
