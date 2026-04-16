from app.db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = Column(String(15), nullable=False, unique=True)
    password = Column(String(15), nullable=False)
    nombre = Column(String(15), nullable=False)
    apellido = Column(String(15), nullable=False)
    direccion = Column(String(255))
    telefono = Column(String(10), nullable=False)
    correo = Column(String(127), nullable=False, unique=True)
    antiguedad = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    estado = Column(Boolean, nullable=False, default=False)
    venta = relationship("Venta", backref="usuario", cascade="delete, merge")