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
    correo:str
    antiguedad:datetime = datetime.now()

# Modelo para obtener el id del usuario
class IdUsuario(BaseModel):
    valor:int