from app.db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    usuario = Column(String(15), nullable=False)
    clave = Column(String(15), nullable=False)
    nombre = Column(String(15), nullable=False)
    apellido = Column(String(15), nullable=False)
    direccion = Column(String(255), nullable=False)
    telefono = Column(String(10), nullable=False)
    correo = Column(String(127), nullable=False, unique=True)
    antiguedad = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    estado = Column(Boolean, nullable=False, default=True)
    venta = relationship("Venta", backref="usuario", cascade="delete, merge")

class Venta(Base):
    __tablename__ = "venta"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    venta = Column(Integer, nullable=False)
    ventas_productos = Column(Integer, nullable=False)