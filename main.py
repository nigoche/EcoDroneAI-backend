from fastapi import FastAPI         # Imports para crear el api con FastAPI,
import uvicorn                      # y uvicorn para correr el api en un servidor local
from pydantic import BaseModel      # Importa el modelo de pydantic
from typing import Optional         # Importa el tipo de dato opcional
from datetime import datetime       # Importa la clase datetime para manejar fechas y horas

# Modelo para un usuario    
class Usuario(BaseModel):  # Esquema de datos para un usuario
    id:int
    nombre:str
    apellido:str
    direccion:Optional[str] = None
    telefono:int
    antiguedad:datetime = datetime.now()

app = FastAPI()

@app.get("/ruta1")
def ruta1():
    return {"mensaje": "Ruta de prueba en mi primera api"}

@app.post("/ruta2")
def ruta2(user:Usuario):
    datos_usuario = user.model_dump()
    print(datos_usuario)
    print(user.nombre)
    print(user.apellido)
    return True

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)