import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from database import get_db
from models import Organizacion, Queja, Usuario, TerminosCondiciones, AvisoPrivacidad, Algoritmo, Hospital
from schemas import OrganizacionResponse, QuejaCreate, QuejaResponse, TerminosResponse, AvisoResponse, AlgoritmoResponse, HospitalResponse, SignosSintomasRequest
from dependencies import get_current_user

router = APIRouter(prefix="/public", tags=["Public"])


# ── ORGANIZACION ─────────────────────────────────────────────────────────────

@router.get("/organizacion", response_model=OrganizacionResponse)
async def obtener_organizacion(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organizacion).order_by(Organizacion.id_organizacion))
    org = result.scalars().first()
    if not org:
        # Create a default empty one if none exists so frontend doesn't crash on 404
        org = Organizacion(nombre="ToxInfo", correo="admin@toxinfo.com", telefono="000-000-0000")
        db.add(org)
        await db.commit()
        await db.refresh(org)
    return org


# ── QUEJAS ───────────────────────────────────────────────────────────────────

@router.post("/quejas", response_model=QuejaResponse, status_code=status.HTTP_201_CREATED)
async def crear_queja(
    datos: QuejaCreate,
    db: AsyncSession = Depends(get_db),
    # Haciendo current_user opcional mediante un try-except o lógica interna, 
    # pero como depends lanza 401, lo dejamos sin validación estricta si es público
    # o usamos la lógica de Pydantic. Si se envían como usuarios registrados, podemos capturarlo.
):
    nueva_queja = Queja(mensaje=datos.mensaje)
    db.add(nueva_queja)
    await db.commit()
    await db.refresh(nueva_queja)
    return nueva_queja

@router.post("/quejas/auth", response_model=QuejaResponse, status_code=status.HTTP_201_CREATED)
async def crear_queja_auth(
    datos: QuejaCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nueva_queja = Queja(mensaje=datos.mensaje, id_usuario=current_user["id_usuario"])
    db.add(nueva_queja)
    await db.commit()
    await db.refresh(nueva_queja)
    return nueva_queja

# ── TERMINOS Y CONDICIONES ───────────────────────────────────────────────────

@router.get("/terminos", response_model=TerminosResponse)
async def obtener_terminos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TerminosCondiciones).order_by(TerminosCondiciones.id_termino))
    terminos = result.scalars().first()
    if not terminos:
        # Create a default empty one if none exists
        terminos = TerminosCondiciones(contenido="[Contenido de Términos y Condiciones no definido]")
        db.add(terminos)
        await db.commit()
        await db.refresh(terminos)
    return terminos

# ── AVISOS DE PRIVACIDAD ─────────────────────────────────────────────────────

@router.get("/avisos", response_model=AvisoResponse)
async def obtener_avisos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AvisoPrivacidad).order_by(AvisoPrivacidad.id_aviso))
    avisos = result.scalars().first()
    if not avisos:
        avisos = AvisoPrivacidad(contenico="[Contenido de Aviso de Privacidad no definido]")
        db.add(avisos)
        await db.commit()
        await db.refresh(avisos)
    return avisos

# ── ALGORITMOS ─────────────────────────────────────────────────────────────

@router.get("/algoritmos", response_model=list[AlgoritmoResponse])
async def obtener_algoritmos(categoria: Optional[str] = None, subcategoria: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Algoritmo).options(selectinload(Algoritmo.hotspots)).where(Algoritmo.activo == True)
    if categoria:
        query = query.where(Algoritmo.categoria == categoria)
    if subcategoria:
        query = query.where(Algoritmo.subcategoria == subcategoria)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/algoritmos/{id_algoritmo}", response_model=AlgoritmoResponse)
async def obtener_algoritmo(id_algoritmo: int, db: AsyncSession = Depends(get_db)):
    query = select(Algoritmo).options(selectinload(Algoritmo.hotspots)).where(Algoritmo.id_algoritmo == id_algoritmo)
    result = await db.execute(query)
    algoritmo = result.scalars().first()
    if not algoritmo:
        raise HTTPException(status_code=404, detail="Algoritmo no encontrado")
    return algoritmo


@router.post("/algoritmos/por-signos", response_model=list[AlgoritmoResponse])
async def obtener_algoritmos_por_signos(body: SignosSintomasRequest, db: AsyncSession = Depends(get_db)):
    signos_usuario = [s.strip().lower() for s in body.signos]
    query = select(Algoritmo).options(selectinload(Algoritmo.hotspots)).where(Algoritmo.activo == True)
    result = await db.execute(query)
    algoritmos = result.scalars().all()

    def contar_coincidencias(algo):
        if not algo.signos_sintomas:
            return 0
        try:
            signos_algo = json.loads(algo.signos_sintomas)
            signos_algo = [s.strip().lower() for s in signos_algo]
        except (json.JSONDecodeError, TypeError):
            return 0
        return sum(1 for s in signos_usuario if s in signos_algo)

    algoritmos_con_match = [(algo, contar_coincidencias(algo)) for algo in algoritmos]
    algoritmos_con_match = [(algo, c) for algo, c in algoritmos_con_match if c > 0]
    algoritmos_con_match.sort(key=lambda x: x[1], reverse=True)

    return [algo for algo, _ in algoritmos_con_match]


# ── HOSPITALES (PÚBLICO) ─────────────────────────────────────────────────────

@router.get("/hospitales", response_model=list[HospitalResponse])
async def obtener_hospitales_publico(estado: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Hospital).order_by(Hospital.nombre)
    if estado:
        query = query.where(Hospital.estado == estado)
    result = await db.execute(query)
    return result.scalars().all()
