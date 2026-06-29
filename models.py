from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime
from database import Base


class Rol(Base):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column("estatus", String(100), nullable=True)
    especialidad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    id_rol: Mapped[int] = mapped_column(Integer, ForeignKey("rol.id_rol"), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")
    noticias_creadas = relationship("Noticia", back_populates="autor", cascade="all, delete-orphan")
    blogs_creados = relationship("Blog", back_populates="autor", cascade="all, delete-orphan")
    comentarios_blog = relationship("ComentarioBlog", back_populates="autor", cascade="all, delete-orphan")
    reacciones = relationship("ReaccionComentario", back_populates="usuario", cascade="all, delete-orphan")
    quejas = relationship("Queja", back_populates="usuario", cascade="all, delete-orphan")


class Carrusel(Base):
    __tablename__ = "carrusel"

    id_carrusel: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    imagen_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    enlace: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Noticia(Base):
    __tablename__ = "noticia"

    id_noticia: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    imagen_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    fecha_publicacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    autor_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    activo: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)

    autor = relationship("Usuario", back_populates="noticias_creadas")



class Organizacion(Base):
    __tablename__ = "organizacion"

    id_organizacion: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    correo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acerca_de: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Queja(Base):
    __tablename__ = "queja"

    id_queja: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_usuario: Mapped[Optional[int]] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=True)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_envio: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    leida: Mapped[bool] = mapped_column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="quejas")


class TerminosCondiciones(Base):
    __tablename__ = "terminos_condiciones"

    id_termino: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contenido: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    id_organizacion: Mapped[Optional[int]] = mapped_column(ForeignKey("organizacion.id_organizacion"), nullable=True)

class Blog(Base):
    __tablename__ = "blog"

    id_blog: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    imagen_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    fecha_publicacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    activo: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    etiquetas: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    opciones_comentarios: Mapped[str] = mapped_column(String(20), default="permitir", nullable=False)

    autor = relationship("Usuario", back_populates="blogs_creados")
    comentarios = relationship("ComentarioBlog", back_populates="blog", cascade="all, delete-orphan")


class AvisoPrivacidad(Base):
    __tablename__ = "aviso_privacidad"

    id_aviso: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contenico: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Typo in postgres schema
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    id_organizacion: Mapped[Optional[int]] = mapped_column(ForeignKey("organizacion.id_organizacion"), nullable=True)


class ComentarioBlog(Base):
    __tablename__ = "comentario_blog"

    id_comentario: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_blog: Mapped[int] = mapped_column(ForeignKey("blog.id_blog"), nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_comentario: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    activo: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    padre_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comentario_blog.id_comentario"), nullable=True)

    blog = relationship("Blog", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios_blog")
    comentarios_hijos = relationship("ComentarioBlog", backref=backref("padre", remote_side=[id_comentario]), cascade="all, delete-orphan")
    reacciones = relationship("ReaccionComentario", back_populates="comentario", cascade="all, delete-orphan")


class ReaccionComentario(Base):
    __tablename__ = "reaccion_comentario"

    id_reaccion: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_comentario: Mapped[int] = mapped_column(ForeignKey("comentario_blog.id_comentario"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)

    comentario = relationship("ComentarioBlog", back_populates="reacciones")
    usuario = relationship("Usuario", back_populates="reacciones")


class Algoritmo(Base):
    __tablename__ = "algoritmo"

    id_algoritmo: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategoria: Mapped[str] = mapped_column(String(100), nullable=False)
    gravedad: Mapped[str] = mapped_column(String(50), nullable=False)
    imagen_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    signos_sintomas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    se_encuentra: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    toxindromes_principales: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    toxindromes_secundarios: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    hotspots = relationship("AlgoritmoHotspot", back_populates="algoritmo", cascade="all, delete-orphan")


class AlgoritmoHotspot(Base):
    __tablename__ = "algoritmo_hotspot"

    id_hotspot: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_algoritmo: Mapped[int] = mapped_column(ForeignKey("algoritmo.id_algoritmo"), nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    titulo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contenido: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    imagen_detalle_url: Mapped[Optional[str]] = mapped_column("imagen_detalle_url", String(1000), nullable=True)
    algoritmo = relationship("Algoritmo", back_populates="hotspots")


class Hospital(Base):
    __tablename__ = "hospital"

    id_hospital: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column("estatus", String(100), nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    codigo_postal: Mapped[str] = mapped_column(String(20), nullable=False)
    telefono: Mapped[str] = mapped_column(String(50), nullable=False)
    latitud: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitud: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mapa_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sitio_web: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
