import asyncio
from sqlalchemy import text
from database import engine

async def run_migration():
    print("Beginning migration...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE usuario ADD COLUMN avatar_url VARCHAR(1000);"))
            print("Successfully added avatar_url column to usuario.")
        except Exception as e:
            if "already exists" in str(e):
                print("Column avatar_url already exists.")
            else:
                print("Error:", e)

if __name__ == "__main__":
    asyncio.run(run_migration())
