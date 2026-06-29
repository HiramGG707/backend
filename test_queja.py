import asyncio
from database import AsyncSessionLocal
from models import Queja

async def test():
    async with AsyncSessionLocal() as db:
        try:
            nueva_queja = Queja(mensaje="Probando un mensaje muy importante 12345")
            db.add(nueva_queja)
            await db.commit()
            await db.refresh(nueva_queja)
            print("OK", nueva_queja.id_queja, nueva_queja.fecha_envio)
        except Exception as e:
            print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test())
