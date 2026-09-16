# Главное приложение с добавлением тестовых рецептов
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import (
    AsyncSessionLocal,
    Recipe,
    engine,
    init_db,
    populate_initial_recipes,
)
from app.schemas import RecipeCreate, RecipeDetail, RecipeOut


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    await populate_initial_recipes()
    yield
    await engine.dispose()


app = FastAPI(
    title="Кулинарная книга",
    description="API для управления рецептами",
    version="1.0.0",
    lifespan=lifespan,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/recipes", response_model=List[RecipeOut])
async def get_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recipe).order_by(Recipe.views_count.desc(), Recipe.cooking_time.asc())
    )
    recipes = result.scalars().all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=RecipeDetail)
async def get_recipe_detail(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )
    await db.execute(
        update(Recipe)
        .where(Recipe.id == recipe_id)
        .values(views_count=Recipe.views_count + 1)
    )
    await db.commit()
    await db.refresh(recipe)
    return recipe


@app.post("/recipes", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
    db_recipe = Recipe(
        name=recipe.name,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        description=recipe.description,
        views_count=0,
    )
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe
