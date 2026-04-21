"""
Configuración de la conexión a la base de datos PostgreSQL utilizando SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://jesusgn:4tac00s;@localhost:5432/fastapi_psql"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
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