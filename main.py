"""
Punto de entrada principal de la aplicación FastAPI.
Configura la conexión a la base de datos, registra los enrutadores
y monta el servidor de archivos estáticos para la galería.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path

from app.routers import user, auth, vuelos, detecciones, archivos
from app.db.database import Base, engine

# ---------------------------------------------------------------------------
# Crear tablas en la BD al iniciar
# ---------------------------------------------------------------------------
def crear_tablas():
    """Crea las tablas en la base de datos si no existen utilizando SQLAlchemy."""
    Base.metadata.create_all(bind=engine)

crear_tablas()

# ---------------------------------------------------------------------------
# Aplicación FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="EcoDrone AI API",
    description=(
        "API para el sistema EcoDrone AI de detección de residuos plásticos con drones. "
        "Incluye gestión de usuarios/operadores, registro de vuelos, detecciones del "
        "modelo YOLO v8 y galería multimedia."
    ),
    version="0.2.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(vuelos.router)
app.include_router(detecciones.router)
app.include_router(archivos.router)

# ---------------------------------------------------------------------------
# Archivos estáticos (galería local — desarrollo)
# Accesibles en: GET /uploads/{nombre_archivo}
# En producción reemplazar por Cloudinary y eliminar este bloque.
# ---------------------------------------------------------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"], summary="Estado de la API")
def root():
    return {"estado": "activo", "version": "0.2.0", "app": "EcoDrone AI API"}

# ---------------------------------------------------------------------------
# Punto de entrada local
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)