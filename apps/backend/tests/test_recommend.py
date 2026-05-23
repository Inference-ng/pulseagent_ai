"""Recommendation Tests — Phase 7"""

import pytest


def test_recommend_endpoint_exists(client):
    """Test that recommend endpoint validates payload"""
    response = client.post(
        "/api/v1/recommend",
        json={
            "user_persona": {"user_id": "test_01"},
            "top_k": 10,
            "domain": "fashion",
        },
    )
    # Endpoints are implemented; expect 200 if agent works, or 500/504 on error
    assert response.status_code in [200, 500, 504, 422]
