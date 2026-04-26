"""
Configuración de la conexión a la base de datos PostgreSQL utilizando SQLAlchemy.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está definida.")

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def obtener_bd():
    """
    Dependencia que proporciona una sesión de base de datos a las solicitudes de FastAPI.
    Garantiza que la sesión se cierre una vez terminada la petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()