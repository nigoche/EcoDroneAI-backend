"""
Punto de entrada principal de la aplicación FastAPI.
Configura la conexión a la base de datos y registra los enrutadores.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import user, auth
from app.db.database import Base, engine

def crear_tablas():
    """Crea las tablas en la base de datos si no existen utilizando SQLAlchemy."""
    Base.metadata.create_all(bind=engine)

crear_tablas()

app = FastAPI(title="EcoDrone AI API", description="API para el manejo de usuarios y autenticación")
app.include_router(user.router)
app.include_router(auth.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # * para todo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)