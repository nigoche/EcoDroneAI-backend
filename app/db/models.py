from app.db.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = Column(String(15), nullable=False, unique=True)
    password = Column(String(15), nullable=False)
    nombre = Column(String(15), nullable=False)
    telefono = Column(String(10), nullable=False)
    correo = Column(String(127), nullable=False, unique=True)