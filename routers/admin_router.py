import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List

from database import get_db

from models import (
    Noticia, Carrusel, Organizacion, Queja, 
    TerminosCondiciones, AvisoPrivacidad, Blog, ComentarioBlog, ReaccionComentario,
    Algoritmo, AlgoritmoHotspot, Hospital
)

from schemas import (
    NoticiaCreate, NoticiaResponse,
    CarruselCreate, CarruselResponse,
    OrganizacionUpdate, OrganizacionResponse,
    QuejaResponse, TerminosResponse, TerminosUpdate,
    AvisoResponse, AvisoUpdate,
    BlogCreate, BlogResponse, ComentarioCreate, ComentarioResponse, ReaccionResponse,
    AlgoritmoCreate, AlgoritmoResponse, AlgoritmoHotspotCreate, AlgoritmoHotspotResponse,
    HospitalCreate, HospitalResponse
)
from pydantic import BaseModel

from dependencies import get_current_admin_user, get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

# Directorio donde se guardan las imágenes subidas
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── UPLOAD IMAGEN ─────────────────────────────────────────────────────────────

@router.post("/upload-imagen")
async def upload_imagen(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_admin_user)
):
    """Sube una imagen al servidor y retorna su URL pública."""
    # Tipos de archivo permitidos o "octet-stream" en caso de que Flutter no envíe el MIME correcto
    ALLOWED_TYPES = {
        "image/jpeg", "image/jpg", "image/png", 
        "image/webp", "image/gif", "image/heic", "image/heif",
        "application/octet-stream"
    }
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES and not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. Use un formato de imagen válido."
        )

    # Generar nombre único para evitar colisiones
    ext = os.path.splitext(file.filename or "imagen.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Guardar el archivo
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    return {"url": f"/static/uploads/{filename}"}

# ── CARRUSEL ─────────────────────────────────────────────────────────────────

@router.get("/carrusel", response_model=List[CarruselResponse])
async def obtener_carrusel(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Carrusel).order_by(Carrusel.orden))
    return result.scalars().all()

@router.post("/carrusel", response_model=CarruselResponse, status_code=status.HTTP_201_CREATED)
async def crear_carrusel(item: CarruselCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    nuevo_item = Carrusel(**item.model_dump())
    db.add(nuevo_item)
    await db.commit()
    await db.refresh(nuevo_item)
    return nuevo_item

@router.put("/carrusel/{item_id}", response_model=CarruselResponse)
async def actualizar_carrusel(item_id: int, item: CarruselCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Carrusel).where(Carrusel.id_carrusel == item_id))
    carrusel_item = result.scalars().first()
    if not carrusel_item:
        raise HTTPException(status_code=404, detail="Item del carrusel no encontrado")
        
    for key, value in item.model_dump().items():
        setattr(carrusel_item, key, value)
        
    await db.commit()
    await db.refresh(carrusel_item)
    return carrusel_item

@router.delete("/carrusel/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_carrusel(item_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Carrusel).where(Carrusel.id_carrusel == item_id))
    carrusel_item = result.scalars().first()
    if not carrusel_item:
        raise HTTPException(status_code=404, detail="Item del carrusel no encontrado")
        
    await db.delete(carrusel_item)
    await db.commit()

# ── NOTICIAS ─────────────────────────────────────────────────────────────────

@router.get("/noticias", response_model=List[NoticiaResponse])
async def obtener_noticias(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Noticia).order_by(Noticia.fecha_publicacion.desc()))
    return result.scalars().all()

@router.post("/noticias", response_model=NoticiaResponse, status_code=status.HTTP_201_CREATED)
async def crear_noticia(item: NoticiaCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    nueva_noticia = Noticia(**item.model_dump(), autor_id=current_user["id_usuario"])
    db.add(nueva_noticia)
    await db.commit()
    await db.refresh(nueva_noticia)
    return nueva_noticia

@router.put("/noticias/{item_id}", response_model=NoticiaResponse)
async def actualizar_noticia(item_id: int, item: NoticiaCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Noticia).where(Noticia.id_noticia == item_id))
    noticia = result.scalars().first()
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
        
    for key, value in item.model_dump().items():
        setattr(noticia, key, value)
        
    await db.commit()
    await db.refresh(noticia)
    return noticia

@router.delete("/noticias/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_noticia(item_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Noticia).where(Noticia.id_noticia == item_id))
    noticia = result.scalars().first()
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    await db.delete(noticia)
    await db.commit()

# ── ORGANIZACION (ADMIN) ─────────────────────────────────────────────────────

@router.put("/organizacion", response_model=OrganizacionResponse)
async def actualizar_organizacion(
    datos: OrganizacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    result = await db.execute(select(Organizacion).order_by(Organizacion.id_organizacion))
    org = result.scalars().first()
    
    if not org:
        # Create it if it doesn't exist
        org = Organizacion()
        db.add(org)
        
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(org, key, value)
        
    await db.commit()
    await db.refresh(org)
    return org

# ── QUEJAS (ADMIN) ───────────────────────────────────────────────────────────

@router.get("/quejas", response_model=List[QuejaResponse])
async def obtener_quejas(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    result = await db.execute(select(Queja).order_by(Queja.fecha_envio.desc()))
    return result.scalars().all()

@router.put("/quejas/{id_queja}/leer", response_model=QuejaResponse)
async def marcar_queja_leida(
    id_queja: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    result = await db.execute(select(Queja).where(Queja.id_queja == id_queja))
    queja = result.scalars().first()
    if not queja:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
        
    queja.leida = True
    await db.commit()
    await db.refresh(queja)
    return queja

# ── TERMINOS Y CONDICIONES ───────────────────────────────────────────────────

@router.put("/terminos", response_model=TerminosResponse)
async def update_terminos(
    datos: TerminosUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user)
):
    result = await db.execute(select(TerminosCondiciones).order_by(TerminosCondiciones.id_termino))
    terminos = result.scalars().first()
    
    if not terminos:
        terminos = TerminosCondiciones(contenido=datos.contenido)
        db.add(terminos)
    else:
        terminos.contenido = datos.contenido

    await db.commit()
    await db.refresh(terminos)
    return terminos


# ── BLOGS ────────────────────────────────────────────────────────────────────

@router.get("/blogs", response_model=List[BlogResponse])
async def obtener_blogs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Blog)
        .options(
            joinedload(Blog.autor),
            selectinload(Blog.comentarios).joinedload(ComentarioBlog.autor),
            selectinload(Blog.comentarios).selectinload(ComentarioBlog.reacciones)
        )
        .order_by(Blog.fecha_publicacion.desc())
    )
    return result.scalars().unique().all()

@router.post("/blogs", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
async def crear_blog(item: BlogCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    nuevo_blog = Blog(**item.model_dump(exclude_unset=True), autor_id=current_user["id_usuario"])
    db.add(nuevo_blog)
    await db.commit()
    await db.refresh(nuevo_blog)
    
    stmt = (
        select(Blog)
        .options(
            joinedload(Blog.autor),
            selectinload(Blog.comentarios).joinedload(ComentarioBlog.autor),
            selectinload(Blog.comentarios).selectinload(ComentarioBlog.reacciones)
        )
        .where(Blog.id_blog == nuevo_blog.id_blog)
    )
    res = await db.execute(stmt)
    return res.scalars().first()

@router.put("/blogs/{item_id}", response_model=BlogResponse)
async def actualizar_blog(item_id: int, item: BlogCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    stmt = (
        select(Blog)
        .options(
            joinedload(Blog.autor),
            selectinload(Blog.comentarios).joinedload(ComentarioBlog.autor),
            selectinload(Blog.comentarios).selectinload(ComentarioBlog.reacciones)
        )
        .where(Blog.id_blog == item_id)
    )
    result = await db.execute(stmt)
    blog = result.scalars().first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog no encontrado")
        
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(blog, key, value)
        
    await db.commit()
    await db.refresh(blog)
    return blog

@router.post("/blogs/{id_blog}/comentarios", response_model=ComentarioResponse, status_code=status.HTTP_201_CREATED)
async def comentar_blog(
    id_blog: int,
    item: ComentarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    blog_result = await db.execute(select(Blog).where(Blog.id_blog == id_blog))
    if not blog_result.scalars().first():
        raise HTTPException(status_code=404, detail="Blog no encontrado")
        
    nuevo_comentario = ComentarioBlog(
        id_blog=id_blog,
        padre_id=item.padre_id,
        autor_id=current_user["id_usuario"],
        contenido=item.contenido
    )
    db.add(nuevo_comentario)
    await db.commit()
    await db.refresh(nuevo_comentario)
    
    stmt = (
        select(ComentarioBlog)
        .options(joinedload(ComentarioBlog.autor), selectinload(ComentarioBlog.reacciones))
        .where(ComentarioBlog.id_comentario == nuevo_comentario.id_comentario)
    )
    res = await db.execute(stmt)
    return res.scalars().first()

class ReaccionRequest(BaseModel):
    tipo: str  # "like" o "dislike"

@router.post("/comentarios/{id_comentario}/reaccion", response_model=ReaccionResponse)
async def reaccionar_comentario(
    id_comentario: int,
    item: ReaccionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(select(ComentarioBlog).where(ComentarioBlog.id_comentario == id_comentario))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    result = await db.execute(
        select(ReaccionComentario)
        .where(ReaccionComentario.id_comentario == id_comentario)
        .where(ReaccionComentario.id_usuario == current_user["id_usuario"])
    )
    reaccion = result.scalars().first()

    if reaccion:
        if reaccion.tipo == item.tipo:
            await db.delete(reaccion)
            await db.commit()
            return ReaccionResponse(id_reaccion=-1, id_comentario=id_comentario, id_usuario=current_user["id_usuario"], tipo="none")
        else:
            reaccion.tipo = item.tipo
            await db.commit()
            await db.refresh(reaccion)
            return reaccion
    else:
        nueva_reaccion = ReaccionComentario(
            id_comentario=id_comentario,
            id_usuario=current_user["id_usuario"],
            tipo=item.tipo
        )
        db.add(nueva_reaccion)
        await db.commit()
        await db.refresh(nueva_reaccion)
        return nueva_reaccion

@router.delete("/blogs/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_blog(item_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Blog).where(Blog.id_blog == item_id))
    blog = result.scalars().first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog no encontrado")
        
    await db.delete(blog)
    await db.commit()


# ── AVISOS DE PRIVACIDAD ─────────────────────────────────────────────────────

@router.put("/avisos", response_model=AvisoResponse)
async def update_avisos(
    datos: AvisoUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user)
):
    result = await db.execute(select(AvisoPrivacidad).order_by(AvisoPrivacidad.id_aviso))
    avisos = result.scalars().first()
    
    if not avisos:
        avisos = AvisoPrivacidad(contenico=datos.contenico)
        db.add(avisos)
    else:
        avisos.contenico = datos.contenico

    await db.commit()
    await db.refresh(avisos)
    return avisos

# ── ALGORITMOS (ADMIN) ───────────────────────────────────────────────────────

@router.post("/algoritmos", response_model=AlgoritmoResponse, status_code=status.HTTP_201_CREATED)
async def crear_algoritmo(item: AlgoritmoCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    nuevo_algo = Algoritmo(**item.model_dump())
    db.add(nuevo_algo)
    await db.commit()
    await db.refresh(nuevo_algo)
    
    stmt = select(Algoritmo).options(selectinload(Algoritmo.hotspots)).where(Algoritmo.id_algoritmo == nuevo_algo.id_algoritmo)
    res = await db.execute(stmt)
    return res.scalars().first()

@router.put("/algoritmos/{item_id}", response_model=AlgoritmoResponse)
async def actualizar_algoritmo(item_id: int, item: AlgoritmoCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Algoritmo).where(Algoritmo.id_algoritmo == item_id))
    algo = result.scalars().first()
    if not algo:
        raise HTTPException(status_code=404, detail="Algoritmo no encontrado")
        
    for key, value in item.model_dump().items():
        setattr(algo, key, value)
        
    await db.commit()
    await db.refresh(algo)
    
    stmt = select(Algoritmo).options(selectinload(Algoritmo.hotspots)).where(Algoritmo.id_algoritmo == algo.id_algoritmo)
    res = await db.execute(stmt)
    return res.scalars().first()

@router.delete("/algoritmos/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_algoritmo(item_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Algoritmo).where(Algoritmo.id_algoritmo == item_id))
    algo = result.scalars().first()
    if not algo:
        raise HTTPException(status_code=404, detail="Algoritmo no encontrado")
    await db.delete(algo)
    await db.commit()

@router.post("/algoritmos/{item_id}/hotspots", response_model=list[AlgoritmoHotspotResponse])
async def mapear_hotspots(item_id: int, hotspots: List[AlgoritmoHotspotCreate], db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Algoritmo).where(Algoritmo.id_algoritmo == item_id))
    algo = result.scalars().first()
    if not algo:
        raise HTTPException(status_code=404, detail="Algoritmo no encontrado")
        
    result_old = await db.execute(select(AlgoritmoHotspot).where(AlgoritmoHotspot.id_algoritmo == item_id))
    viejos = result_old.scalars().all()
    for v in viejos:
        await db.delete(v)
        
    for h in hotspots:
        nuevo_hotspot = AlgoritmoHotspot(**h.model_dump(), id_algoritmo=item_id)
        db.add(nuevo_hotspot)
        
    await db.commit()
    
    result_new = await db.execute(select(AlgoritmoHotspot).where(AlgoritmoHotspot.id_algoritmo == item_id))
    return result_new.scalars().all()


# ── HOSPITALES (ADMIN) ───────────────────────────────────────────────────────

@router.get("/hospitales", response_model=List[HospitalResponse])
async def obtener_hospitales(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hospital).order_by(Hospital.fecha_registro.desc()))
    return result.scalars().all()

@router.post("/hospitales", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
async def crear_hospital(item: HospitalCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    nuevo_hospital = Hospital(**item.model_dump())
    db.add(nuevo_hospital)
    await db.commit()
    await db.refresh(nuevo_hospital)
    return nuevo_hospital

@router.put("/hospitales/{item_id}", response_model=HospitalResponse)
async def actualizar_hospital(item_id: int, item: HospitalCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Hospital).where(Hospital.id_hospital == item_id))
    hospital = result.scalars().first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")
        
    for key, value in item.model_dump().items():
        setattr(hospital, key, value)
        
    await db.commit()
    await db.refresh(hospital)
    return hospital

@router.delete("/hospitales/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_hospital(item_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    result = await db.execute(select(Hospital).where(Hospital.id_hospital == item_id))
    hospital = result.scalars().first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")
    await db.delete(hospital)
    await db.commit()
