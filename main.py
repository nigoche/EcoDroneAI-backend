from fastapi import FastAPI         # Importa FastAPI para crear el api con FastAPI,
import uvicorn                      # y uvicorn para correr el api en un servidor local
from app.routers import user

app = FastAPI()
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)