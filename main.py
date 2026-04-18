
from fastapi import FastAPI
import uvicorn
from app.routers import user
from app.db.database import Base, engine

def crear_tablas():
    Base.metadata.create_all(bind=engine)

crear_tablas()

app = FastAPI()
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)