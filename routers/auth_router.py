from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from datetime import datetime, timezone
import os

from database import get_db
from models import Usuario, Rol
from schemas import (
    LoginRequest, RegisterRequest, SocialLoginRequest,
    TokenResponse, UserResponse,
)
from auth import hash_password, verify_password, create_access_token
from firebase_init import verify_firebase_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

DEFAULT_ROL_ID = int(os.getenv("DEFAULT_USER_ROL_ID", "2"))


# ── POST /auth/login ───────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Buscar usuario por email
    result = await db.execute(
        select(Usuario).where(Usuario.email == credentials.email)
    )
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    if usuario.status not in (None, 'activo'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está deshabilitada. Contacta al administrador.",
        )

    if not verify_password(credentials.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    # Actualizar último acceso
    usuario.ultimo_acceso = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(usuario)

    # Generar token JWT
    token = create_access_token(
        data={"sub": str(usuario.id_usuario), "email": usuario.email, "rol": usuario.id_rol}
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(usuario),
    )


# ── POST /auth/register ────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(datos: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Verificar que el email no esté ya registrado
    result = await db.execute(
        select(Usuario).where(Usuario.email == datos.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo electrónico",
        )

    # Verificar que el rol por defecto existe
    rol_result = await db.execute(
        select(Rol).where(Rol.id_rol == DEFAULT_ROL_ID)
    )
    if not rol_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rol por defecto (id={DEFAULT_ROL_ID}) no encontrado. "
                   "Actualiza DEFAULT_USER_ROL_ID en el .env",
        )

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=datos.email,
        telefono=datos.telefono,
        password_hash=hash_password(datos.password),
        estado=datos.estado,
        especialidad=datos.especialidad,
        status='activo',
        id_rol=DEFAULT_ROL_ID,
        fecha_registro=datetime.now(timezone.utc),
    )

    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)

    return UserResponse.model_validate(nuevo_usuario)


# ── POST /auth/social ──────────────────────────────────────────────────────────

@router.post("/social", response_model=TokenResponse)
async def social_login(
    datos: SocialLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        decoded = verify_firebase_token(datos.id_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    firebase_uid = decoded.get("uid", "")
    email = decoded.get("email", "")
    name = decoded.get("name", "")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El proveedor no devolvió un correo electrónico",
        )

    # Try to find existing user by email
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    usuario = result.scalar_one_or_none()

    if not usuario:
        # Parse name into nombre/apellido
        nombre = name
        apellido = ""
        if name and " " in name.strip():
            parts = name.strip().rsplit(" ", 1)
            nombre = parts[0]
            apellido = parts[1] if len(parts) > 1 else ""

        if not nombre:
            nombre = email.split("@")[0]
            apellido = ""

        # Check if rol exists
        rol_result = await db.execute(
            select(Rol).where(Rol.id_rol == DEFAULT_ROL_ID)
        )
        if not rol_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rol por defecto (id={DEFAULT_ROL_ID}) no encontrado",
            )

        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password_hash="",  # No password for social login users
            status="activo",
            id_rol=DEFAULT_ROL_ID,
            fecha_registro=datetime.now(timezone.utc),
        )
        db.add(usuario)
        await db.commit()
        await db.refresh(usuario)

    if usuario.status not in (None, "activo"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está deshabilitada. Contacta al administrador.",
        )

    # Update last access
    usuario.ultimo_acceso = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(usuario)

    # Generate JWT
    token = create_access_token(
        data={
            "sub": str(usuario.id_usuario),
            "email": usuario.email,
            "rol": usuario.id_rol,
        }
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(usuario),
    )
