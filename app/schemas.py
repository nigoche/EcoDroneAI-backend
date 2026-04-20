from pydantic import BaseModel      # Importa el modelo de pydantic
from typing import Optional         # Importa el tipo de dato opcional
from datetime import datetime       # Importa la clase datetime para manejar fechas y horas

# Modelo para un usuario    
class Usuario(BaseModel):  # Esquema de datos para un usuario
    username:str
    password:str
    nombre:str
    telefono:int
    correo:str

# Modelo para actualizar la información de un usuario    
class ActualizarUsuario(BaseModel):
    username: str = None
    password: str = None
    nombre: str = None
    telefono: int = None
    correo: str = None

# Modelo para devolver información concreta de un usuario
class InfoUsuario(BaseModel):
    username:str
    nombre:str
    telefono:int
    correo:str
    class Config():
        from_attributes = True

# ---------------------------------------------------------------------------
# Schemas de autenticación
# ---------------------------------------------------------------------------

# Credenciales que el cliente envía para iniciar sesión
class LoginRequest(BaseModel):
    username: str
    password: str

# Respuesta que devuelve el servidor tras un login exitoso
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
