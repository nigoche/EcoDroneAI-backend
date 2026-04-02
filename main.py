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

# Modelo para obtener el id del usuario
class IdUsuario(BaseModel):
    valor:int

usuarios = []

app = FastAPI()

@app.get("/ruta1")
def ruta1():
    return {"mensaje": "Ruta de prueba en mi primera api"}

@app.get("/usuarios")
def obtener_usuarios():
    return usuarios

@app.post("/usuarios")
def crear_usuario(user:Usuario):
    usuario = user.model_dump()
    usuarios.append(usuario)
    return {"respuesta": "Usuario creado con éxito"}

@app.post("/usuarios/id/{id_usuario}")     # Endpoint corregido
def obtener_usuario_por_id_en_url(id_usuario:int):
    for usuario in usuarios:
       if usuario["id"] == id_usuario:
           return {"usuario": usuario}
    return {"respuesta": "Usuario no encontrado"}

# Segundo método para obtener un usuario por id sin usar un path parameter, sino un body parameter
# Este endpoint no funcionará si existe el endpoint anterior, ya que ambos tienen la misma ruta al inicio (/usuarios) y FastAPI no sabrá a cuál de los dos endpoints dirigirse cuando se haga una petición a esa ruta, ya que una espera por un número en la ruta y la otra espera por un JSON en el body, lo que generará un conflicto
# Para solucionar esto, se puede cambiar la ruta del endpoint anterior a algo como "/usuarios/id/{id_usuario}" o eliminarlo completamente
@app.post("/usuarios/info")
def obtener_usuario_por_id_en_json(id_usuario:IdUsuario):
    for user in usuarios:
       if user["id"] == id_usuario.valor:
           return {"usuario": user}
    return {"respuesta": "Usuario no encontrado"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)