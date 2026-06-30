import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth_router, admin_router, users_router, public_router

app = FastAPI(
    title="ToxInfo API",
    description="Backend de autenticación para la app ToxInfo",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    from database import engine, Base
    import models
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Tablas sincronizadas/creadas en la base de datos.")
    except Exception as e:
        print(f"Error al sincronizar tablas al iniciar: {e}")

# ── CORS ───────────────────────────────────────────────────────────────────────
# Permite peticiones desde el simulador iOS (localhost) y el emulador Android (10.0.2.2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción reemplaza por URLs específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rutas ──────────────────────────────────────────────────────────────────────
app.include_router(public_router.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(users_router.router)

# ── Archivos estáticos (imágenes subidas) ──────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": "ToxInfo API v1.0"}
