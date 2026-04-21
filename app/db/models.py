"""
Modelos ORM de SQLAlchemy que representan las tablas en la base de datos.
"""
from app.db.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from datetime import datetime

class Usuario(Base):
    """Modelo ORM para la tabla 'usuario' en PostgreSQL."""
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = Column(String(15), nullable=False, unique=True)
    password = Column(String(15), nullable=False)
    nombre = Column(String(15), nullable=False)
    telefono = Column(String(10), nullable=False)
    correo = Column(String(127), nullable=False, unique=True)