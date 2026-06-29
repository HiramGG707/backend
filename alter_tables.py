import asyncio
from database import engine, Base
import models
from sqlalchemy import text

async def main():
    try:
        async with engine.begin() as conn:
            # Add columns to blog
            await conn.execute(text("ALTER TABLE blog ADD COLUMN IF NOT EXISTS etiquetas VARCHAR(500) NULL;"))
            await conn.execute(text("ALTER TABLE blog ADD COLUMN IF NOT EXISTS opciones_comentarios VARCHAR(20) DEFAULT 'permitir' NOT NULL;"))

            # Add columns to comentario_blog
            await conn.execute(text("ALTER TABLE comentario_blog ADD COLUMN IF NOT EXISTS padre_id INTEGER REFERENCES comentario_blog(id_comentario) NULL;"))

            # Add columns to hospital
            await conn.execute(text("ALTER TABLE hospital ADD COLUMN IF NOT EXISTS mapa_url TEXT NULL;"))
            await conn.execute(text("ALTER TABLE hospital ADD COLUMN IF NOT EXISTS sitio_web VARCHAR(500) NULL;"))

            # Add column to algoritmo
            await conn.execute(text("ALTER TABLE algoritmo ADD COLUMN IF NOT EXISTS signos_sintomas TEXT NULL;"))
            await conn.execute(text("ALTER TABLE algoritmo ADD COLUMN IF NOT EXISTS se_encuentra TEXT NULL;"))
            await conn.execute(text("ALTER TABLE algoritmo ADD COLUMN IF NOT EXISTS toxindromes_principales TEXT NULL;"))
            await conn.execute(text("ALTER TABLE algoritmo ADD COLUMN IF NOT EXISTS toxindromes_secundarios TEXT NULL;"))

            # Create ReaccionComentario (and any other missing tables)
            await conn.run_sync(Base.metadata.create_all)

            print("Tablas alteradas y creadas correctamente.")
    except Exception as e:
        print(f"Error al alterar tablas: {e}")

if __name__ == "__main__":
    asyncio.run(main())
