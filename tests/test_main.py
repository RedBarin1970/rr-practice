#  Тесты
import os
import sys

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import AsyncSessionLocal, init_db
from app.main import app

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM recipes"))
        await session.commit()


@pytest.mark.asyncio
async def test_create_recipe():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/recipes",
            json={
                "name": "Тестовый рецепт",
                "cooking_time": 30,
                "ingredients": ["ингредиент 1", "ингредиент 2"],
                "description": "Описание",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Тестовый рецепт"
    assert data["views_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_get_recipes():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/recipes",
            json={
                "name": "Рецепт A",
                "cooking_time": 20,
                "ingredients": ["ингр1"],
                "description": "описание A",
            },
        )
        await ac.post(
            "/recipes",
            json={
                "name": "Рецепт B",
                "cooking_time": 40,
                "ingredients": ["ингр2"],
                "description": "описание B",
            },
        )
        response = await ac.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["cooking_time"] == 20
    assert data[1]["cooking_time"] == 40


@pytest.mark.asyncio
async def test_get_recipe_detail_increments_views():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        create_resp = await ac.post(
            "/recipes",
            json={
                "name": "Популярный рецепт",
                "cooking_time": 15,
                "ingredients": ["ингр"],
                "description": "описание",
            },
        )
        recipe_id = create_resp.json()["id"]
        detail_resp1 = await ac.get(f"/recipes/{recipe_id}")
        assert detail_resp1.status_code == 200
        views1 = detail_resp1.json()["views_count"]
        detail_resp2 = await ac.get(f"/recipes/{recipe_id}")
        views2 = detail_resp2.json()["views_count"]
        assert views2 == views1 + 1


@pytest.mark.asyncio
async def test_get_recipe_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/recipes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"
