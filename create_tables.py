import asyncio
from database import engine, Base
import models
from sqlalchemy import text

async def main():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Tablas creadas correctamente")
    except Exception as e:
        print(f"Error al crear tablas: {e}")

if __name__ == "__main__":
    asyncio.run(main())
