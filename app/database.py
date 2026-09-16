# Настройка БД + добавление трех тестовых рецептов если база пуста
import os

from sqlalchemy import JSON, Integer, String, Text, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./recipes.db")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cooking_time: Mapped[int] = mapped_column(Integer, nullable=False)
    ingredients: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def populate_initial_recipes():
    """Заполняет базу стартовыми рецептами, если она пуста."""
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже записи
        result = await session.execute(select(Recipe))
        existing = result.scalars().first()
        if existing is None:
            sample_recipes = [
                Recipe(
                    name="Классический борщ",
                    cooking_time=120,
                    ingredients=[
                        "свекла",
                        "капуста",
                        "картофель",
                        "морковь",
                        "лук",
                        "томатная паста",
                        "говядина",
                        "соль",
                        "перец",
                    ],
                    description="Сварить бульон, добавить овощи, варить до готовности."
                    " Подавать со сметаной.",
                    views_count=0,
                ),
                Recipe(
                    name="Оливье",
                    cooking_time=60,
                    ingredients=[
                        "картофель",
                        "морковь",
                        "яйца",
                        "колбаса",
                        "огурцы соленые",
                        "горошек консервированный",
                        "майонез",
                    ],
                    description="Отварить овощи и яйца, нарезать кубиками, "
                    "смешать с горошком и майонезом.",
                    views_count=0,
                ),
                Recipe(
                    name="Греческий салат",
                    cooking_time=15,
                    ingredients=[
                        "огурцы",
                        "помидоры",
                        "болгарский перец",
                        "фета",
                        "маслины",
                        "оливковое масло",
                        "орегано",
                    ],
                    description="Нарезать овощи крупными кусками, добавить "
                    "фету и маслины, заправить маслом и орегано.",
                    views_count=0,
                ),
            ]
            session.add_all(sample_recipes)
            await session.commit()
