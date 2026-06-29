from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Usuario
from schemas import UserResponse, UserUpdateRequest, PasswordChangeRequest, EmailChangeRequest
from auth import hash_password, verify_password
from dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["usuarios"])

# Directorio donde se guardan los avatars
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── GET /users/me ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == current_user["id_usuario"]))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# ── PUT /users/me ─────────────────────────────────────────────────────────────

@router.put("/me", response_model=UserResponse)
async def update_me(
    datos: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == current_user["id_usuario"]))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.apellido is not None:
        usuario.apellido = datos.apellido
    if datos.telefono is not None:
        usuario.telefono = datos.telefono
    if datos.estado is not None:
        usuario.estado = datos.estado
    if datos.especialidad is not None:
        usuario.especialidad = datos.especialidad

    await db.commit()
    await db.refresh(usuario)
    return usuario


# ── PUT /users/me/password ────────────────────────────────────────────────────

@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    datos: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == current_user["id_usuario"]))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(datos.current_password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña actual es incorrecta")

    usuario.password_hash = hash_password(datos.new_password)
    await db.commit()
    return {"detail": "Contraseña actualizada correctamente"}


# ── PUT /users/me/email ───────────────────────────────────────────────────────

@router.put("/me/email", response_model=UserResponse)
async def change_email(
    datos: EmailChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == current_user["id_usuario"]))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña incorrecta")

    # Check if new email is already in use
    existing = await db.execute(select(Usuario).where(Usuario.email == datos.new_email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ese correo ya está en uso")

    usuario.email = datos.new_email
    await db.commit()
    await db.refresh(usuario)
    return usuario

# ── POST /users/me/avatar ─────────────────────────────────────────────────────

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == current_user["id_usuario"]))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

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

    ext = os.path.splitext(file.filename or "avatar.jpg")[1] or ".jpg"
    filename = f"avatar_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    usuario.avatar_url = f"/static/uploads/{filename}"
    await db.commit()
    await db.refresh(usuario)

    return usuario


# ── DELETE /users/me ──────────────────────────────────────────────────────────

@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == current_user["id_usuario"]))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si el usuario tiene una foto de perfil (avatar), intentamos borrarla físicamente del servidor.
    if usuario.avatar_url:
        try:
            filename = os.path.basename(usuario.avatar_url)
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error al eliminar archivo de avatar {usuario.avatar_url}: {e}")

    await db.delete(usuario)
    await db.commit()
    return {"detail": "Cuenta eliminada correctamente"}


