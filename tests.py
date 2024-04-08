import pytest
from httpx import AsyncClient

from src.models.routes import Route

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_create_route(test_client: AsyncClient):
    file_path = "sample_points.csv"
    files = {"file": ("sample_points.csv", open(file_path, "rb"), "text/csv")}
    response = test_client.post("/api/routes",  files=files)
    assert response.status_code == 201
    assert "id" in response.json()
    assert "points" in response.json()


@pytest.mark.asyncio
async def test_route(test_client: AsyncClient):
    file_path = "sample_points.csv"
    files = {"file": ("sample_points.csv", open(file_path, "rb"), "text/csv")}
    response = test_client.post("/api/routes",  files=files)
    print(response.json()['points'])
    assert response.status_code == 201
    assert 33.708610696262625 == response.json()['points'][0]['lat']
    assert 173.81376595342067 == response.json()['points'][23]['lng']


@pytest.mark.asyncio
async def test_get_route_by_id(test_client: AsyncClient, sample_route: Route):
    response = test_client.get(f"/api/routes/{sample_route.id}")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "points" in response.json()
