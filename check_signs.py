import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import Algoritmo
from database import DATABASE_URL

async def main():
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Algoritmo))
        algoritmos = result.scalars().all()
        print(f"Total algoritmos: {len(algoritmos)}")
        for algo in algoritmos:
            print(f"- ID: {algo.id_algoritmo}, Título: {algo.titulo}")
            print(f"  Signos: {algo.signos_sintomas}")
            print()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
