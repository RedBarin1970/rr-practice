#
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    name: str = Field(..., max_length=255, description="Название рецепта")
    cooking_time: int = Field(..., gt=0, description="Время готовки в минутах")
    ingredients: List[str] = Field(..., description="Список ингредиентов")
    description: str = Field(..., description="Описание приготовления")


class RecipeOut(BaseModel):
    id: int
    name: str
    views_count: int
    cooking_time: int

    model_config = ConfigDict(from_attributes=True)


class RecipeDetail(RecipeOut):
    ingredients: List[str]
    description: str
