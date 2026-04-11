from pydantic import BaseModel      # Importa el modelo de pydantic
from typing import Optional         # Importa el tipo de dato opcional
from datetime import datetime       # Importa la clase datetime para manejar fechas y horas

# Modelo para un usuario    
class Usuario(BaseModel):  # Esquema de datos para un usuario
    username:str
    password:str
    nombre:str
    apellido:str
    direccion:Optional[str] = None
    telefono:int
    correo:str
    antiguedad:datetime = datetime.now()

# Modelo para actualizar la información de un usuario    
class ActualizarUsuario(BaseModel):
    username: str = None
    password: str = None
    nombre: str = None
    apellido: str = None
    direccion: str = None
    telefono: int = None
    correo: str = None
    antiguedad: datetime = None

# Modelo para devolver información concreta de un usuario
class InfoUsuario(BaseModel):
    username:str
    nombre:str
    apellido:str
    correo:str
    class Config():
        from_attributes = True