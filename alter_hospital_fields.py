import asyncio
from database import engine
from sqlalchemy import text

async def main():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE hospital ADD COLUMN IF NOT EXISTS mapa_url TEXT NULL;"))
            await conn.execute(text("ALTER TABLE hospital ADD COLUMN IF NOT EXISTS sitio_web VARCHAR(500) NULL;"))
            print("Tablas alteradas correctamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
