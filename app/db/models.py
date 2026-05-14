"""
Modelos ORM de SQLAlchemy que representan las tablas en la base de datos.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, Text,
    DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


# ---------------------------------------------------------------------------
# Enumeraciones
# ---------------------------------------------------------------------------

class TipoArchivo(str, enum.Enum):
    imagen = "imagen"
    video = "video"


# ---------------------------------------------------------------------------
# Tabla: usuario (operadores del dron)
# ---------------------------------------------------------------------------

class Usuario(Base):
    """Modelo ORM para la tabla 'usuario' en PostgreSQL."""
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = Column(String(30), nullable=False, unique=True)
    password = Column(String(127), nullable=False)
    correo = Column(String(127), nullable=False, unique=True)

    # Relaciones
    vuelos = relationship("Vuelo", back_populates="operador", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Tabla: vuelo
# ---------------------------------------------------------------------------

class Vuelo(Base):
    """Registro de un vuelo de dron realizado por un operador."""
    __tablename__ = "vuelo"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    operador_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    latitud_inicio = Column(Float, nullable=True)
    longitud_inicio = Column(Float, nullable=True)
    notas = Column(Text, nullable=True)
    sincronizado = Column(Boolean, nullable=False, default=False)

    # Relaciones
    operador = relationship("Usuario", back_populates="vuelos")
    detecciones = relationship("Deteccion", back_populates="vuelo", cascade="all, delete-orphan")
    archivos = relationship("Archivo", back_populates="vuelo", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Tabla: deteccion
# ---------------------------------------------------------------------------

class Deteccion(Base):
    """
    Detección individual de botellas PET realizada por el modelo YOLO v8.
    Cada detección corresponde a un frame/momento durante el vuelo.
    """
    __tablename__ = "deteccion"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    vuelo_id = Column(Integer, ForeignKey("vuelo.id", ondelete="CASCADE"), nullable=False)
    operador_id = Column(Integer, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    cantidad_botellas = Column(Integer, nullable=False, default=1)
    confianza = Column(Float, nullable=False, default=0.0)
    etiqueta = Column(String(50), nullable=False, default="PET")

    # Relaciones
    vuelo = relationship("Vuelo", back_populates="detecciones")
    operador = relationship("Usuario")
    archivos = relationship("Archivo", back_populates="deteccion")


# ---------------------------------------------------------------------------
# Tabla: archivo (galería multimedia)
# ---------------------------------------------------------------------------

class Archivo(Base):
    """
    Archivo multimedia (imagen o video) asociado a un vuelo o detección.
    La URL puede ser local (/uploads/...) o de Cloudinary (https://...).
    """
    __tablename__ = "archivo"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    vuelo_id = Column(Integer, ForeignKey("vuelo.id", ondelete="CASCADE"), nullable=True)
    deteccion_id = Column(Integer, ForeignKey("deteccion.id", ondelete="SET NULL"), nullable=True)
    operador_id = Column(Integer, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True)
    tipo = Column(SAEnum(TipoArchivo), nullable=False, default=TipoArchivo.imagen)
    url = Column(String(500), nullable=False)
    nombre_archivo = Column(String(255), nullable=True)
    tamanio_bytes = Column(Integer, nullable=True)
    fecha_captura = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relaciones
    vuelo = relationship("Vuelo", back_populates="archivos")
    deteccion = relationship("Deteccion", back_populates="archivos")
    operador = relationship("Usuario")