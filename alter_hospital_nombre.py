import asyncio
from database import engine
from sqlalchemy import text

async def main():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE hospital ADD COLUMN nombre VARCHAR(255) NOT NULL DEFAULT 'Hospital';"))
        print("Columna nombre agregada")

if __name__ == "__main__":
    asyncio.run(main())
