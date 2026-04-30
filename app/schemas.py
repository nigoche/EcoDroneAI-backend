from pydantic import BaseModel

# Esquemas de modelos
# ---------------------------------------------------------------------------

class Usuario(BaseModel):
    """Esquema de datos esperado para la creación de un nuevo usuario."""
    username: str
    password: str
    correo: str

class ActualizarUsuario(BaseModel):
    """Esquema de datos para la actualización parcial de la información de un usuario."""
    username: str = None
    password: str = None
    correo: str = None

class InfoUsuario(BaseModel):
    """Esquema para devolver la información pública/básica de un usuario."""
    username: str
    correo: str

    class Config():
        from_attributes = True

# Esquemas de autenticación
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Credenciales enviadas por el cliente para iniciar sesión."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Respuesta devuelta por el servidor tras una autenticación exitosa."""
    access_token: str
    token_type: str = "bearer"