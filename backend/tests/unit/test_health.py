"""Tests for health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.unit
async def test_health_check(client: AsyncClient) -> None:
    """Test health check endpoint.
    
    Args:
        client: Async HTTP client.
    """
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "services" in data
    assert isinstance(data["services"], dict)
