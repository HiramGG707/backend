from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime
from typing import Optional


# ── Profile Update Schemas ─────────────────────────────────────────────

class UserUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None
    especialidad: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("confirm_new_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v

class EmailChangeRequest(BaseModel):
    new_email: EmailStr
    password: str


# ── Request schemas ────────────────────────────────────────────────────────────

class SocialLoginRequest(BaseModel):
    id_token: str
    provider: str = Field(..., pattern=r"^(google|apple)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: Optional[str] = None
    estado: Optional[str] = None
    especialidad: Optional[str] = None
    password: str
    confirmar_password: str

    @field_validator("confirmar_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v

    @field_validator("nombre", "apellido")
    @classmethod
    def no_empty(cls, v):
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío")
        return v.strip()


# ── Response schemas ───────────────────────────────────────────────────────────

class RolResponse(BaseModel):
    id_rol: int
    nombre: str

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str]
    avatar_url: Optional[str] = None
    estado: Optional[str] = None
    especialidad: Optional[str] = None
    status: Optional[str] = "activo"
    id_rol: int
    fecha_registro: Optional[datetime]

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Carrusel Schemas ──────────────────────────────────────────────────────────

class CarruselCreate(BaseModel):
    titulo: str = Field(..., max_length=255)
    imagen_url: str = Field(..., max_length=1000)
    enlace: Optional[str] = Field(None, max_length=1000)
    orden: Optional[int] = 0
    activo: Optional[str] = "activo"

class CarruselResponse(CarruselCreate):
    id_carrusel: int
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


# ── Noticia Schemas ──────────────────────────────────────────────────────────

class NoticiaCreate(BaseModel):
    titulo: str = Field(..., max_length=255)
    contenido: str
    imagen_url: Optional[str] = Field(None, max_length=1000)
    activo: Optional[str] = "activo"

class NoticiaResponse(NoticiaCreate):
    id_noticia: int
    autor_id: int
    fecha_publicacion: datetime

    model_config = {"from_attributes": True}



# ── Organizacion Schemas ──────────────────────────────────────────────────────

class OrganizacionUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    descripcion: Optional[str] = None
    acerca_de: Optional[str] = None

class OrganizacionResponse(BaseModel):
    id_organizacion: int
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    descripcion: Optional[str] = None
    acerca_de: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Queja Schemas ────────────────────────────────────────────────────────────

class QuejaCreate(BaseModel):
    mensaje: str = Field(..., min_length=10)

class QuejaResponse(BaseModel):
    id_queja: int
    id_usuario: Optional[int] = None
    mensaje: str
    fecha_envio: datetime
    leida: bool

    model_config = {"from_attributes": True}


# ── Terminos y Condiciones Schemas ──────────────────────────────────────────

class TerminosUpdate(BaseModel):
    contenido: str

class TerminosResponse(BaseModel):
    id_termino: int
    contenido: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = {"from_attributes": True}

# ── Blog Schemas ─────────────────────────────────────────────────────────────

class AutorResponse(BaseModel):
    nombre: str
    apellido: str

    model_config = {"from_attributes": True}

class ReaccionResponse(BaseModel):
    id_reaccion: int
    id_comentario: int
    id_usuario: int
    tipo: str

    model_config = {"from_attributes": True}

class ComentarioCreate(BaseModel):
    contenido: str = Field(..., min_length=1)
    padre_id: Optional[int] = None

class ComentarioResponse(BaseModel):
    id_comentario: int
    id_blog: int
    autor_id: int
    contenido: str
    fecha_comentario: datetime
    padre_id: Optional[int] = None
    autor: Optional[AutorResponse] = None
    reacciones: list[ReaccionResponse] = []

    model_config = {"from_attributes": True}

class BlogCreate(BaseModel):
    titulo: str = Field(..., max_length=255)
    contenido: str
    imagen_url: Optional[str] = Field(None, max_length=1000)
    activo: Optional[str] = "activo"
    etiquetas: Optional[str] = None
    opciones_comentarios: Optional[str] = "permitir"
    fecha_publicacion: Optional[datetime] = None

class BlogResponse(BlogCreate):
    id_blog: int
    autor_id: int
    fecha_publicacion: Optional[datetime] = None
    etiquetas: Optional[str] = None
    opciones_comentarios: Optional[str] = "permitir"
    autor: Optional[AutorResponse] = None
    comentarios: list[ComentarioResponse] = []

    model_config = {"from_attributes": True}


# ── Aviso de Privacidad Schemas ─────────────────────────────────────────────

class AvisoUpdate(BaseModel):
    contenico: str

class AvisoResponse(BaseModel):
    id_aviso: int
    contenico: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Algoritmo Schemas ─────────────────────────────────────────────

class AlgoritmoHotspotCreate(BaseModel):
    x: float
    y: float
    width: float
    height: float
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    imagen_detalle_url: Optional[str] = None

class AlgoritmoHotspotResponse(AlgoritmoHotspotCreate):
    id_hotspot: int
    id_algoritmo: int

    model_config = {"from_attributes": True}

class AlgoritmoCreate(BaseModel):
    titulo: str = Field(..., max_length=255)
    categoria: str = Field(..., max_length=100)
    subcategoria: str = Field(default="", max_length=100)
    gravedad: str = Field(..., max_length=50)
    imagen_url: str = Field(..., max_length=1000)
    signos_sintomas: Optional[str] = None
    se_encuentra: Optional[str] = None
    toxindromes_principales: Optional[str] = None
    toxindromes_secundarios: Optional[str] = None
    activo: Optional[bool] = True

class AlgoritmoResponse(AlgoritmoCreate):
    id_algoritmo: int
    fecha_creacion: datetime
    hotspots: list[AlgoritmoHotspotResponse] = []

    model_config = {"from_attributes": True}


class SignosSintomasRequest(BaseModel):
    signos: list[str] = []


# ── Hospital Schemas ─────────────────────────────────────────────

class HospitalCreate(BaseModel):
    nombre: str = Field(..., max_length=255)
    estado: str = Field(..., max_length=100)
    ciudad: str = Field(..., max_length=100)
    direccion: str
    codigo_postal: str = Field(..., max_length=20)
    telefono: str = Field(..., max_length=50)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    mapa_url: Optional[str] = None
    sitio_web: Optional[str] = None

class HospitalResponse(HospitalCreate):
    id_hospital: int
    fecha_registro: datetime

    model_config = {"from_attributes": True}
