from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ===========================================================================
# Usuarios / Operadores
# ===========================================================================

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
    id: int
    username: str
    correo: str

    class Config():
        from_attributes = True


# ===========================================================================
# Autenticación
# ===========================================================================

class LoginRequest(BaseModel):
    """Credenciales enviadas por el cliente para iniciar sesión."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Respuesta devuelta por el servidor tras una autenticación exitosa."""
    access_token: str
    token_type: str = "bearer"

class RecuperarPasswordRequest(BaseModel):
    """Correo del usuario que solicita recuperar su contraseña."""
    correo: str


# ===========================================================================
# Vuelos
# ===========================================================================

class VueloCreate(BaseModel):
    """Datos necesarios para registrar un nuevo vuelo."""
    nombre: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    latitud_inicio: Optional[float] = None
    longitud_inicio: Optional[float] = None
    notas: Optional[str] = None

class VueloUpdate(BaseModel):
    """Campos editables de un vuelo (todos opcionales)."""
    nombre: Optional[str] = None
    fecha_fin: Optional[datetime] = None
    notas: Optional[str] = None
    sincronizado: Optional[bool] = None

class VueloOut(BaseModel):
    """Información resumida de un vuelo para la lista/historial."""
    id: int
    nombre: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    latitud_inicio: Optional[float] = None
    longitud_inicio: Optional[float] = None
    sincronizado: bool
    operador: str                   # username del operador
    num_detecciones: int = 0
    num_botellas_total: int = 0

    class Config():
        from_attributes = True

class VueloDetalle(VueloOut):
    """Información completa de un vuelo incluyendo sus detecciones."""
    notas: Optional[str] = None
    detecciones: List["DeteccionOut"] = []


# ===========================================================================
# Detecciones
# ===========================================================================

class DeteccionItem(BaseModel):
    """Un solo frame de detección YOLO (parte del batch)."""
    timestamp: datetime
    latitud: float
    longitud: float
    cantidad_botellas: int = 1
    confianza: float
    etiqueta: str = "PET"

class DeteccionCreate(BaseModel):
    """
    Payload para registrar detecciones de un vuelo.
    Acepta un batch (lista) de detecciones para permitir envío en ráfaga
    desde el modelo YOLO, que puede generar múltiples frames de golpe.
    """
    vuelo_id: int
    detecciones: List[DeteccionItem]

class DeteccionOut(BaseModel):
    """Información de una detección para la pestaña Lista."""
    id: int
    vuelo_id: int
    nombre_vuelo: str
    operador: str
    timestamp: datetime
    latitud: float
    longitud: float
    cantidad_botellas: int
    confianza: float
    etiqueta: str

    class Config():
        from_attributes = True

class PuntoMapa(BaseModel):
    """
    Punto agrupado para mostrar en el mapa.
    Representa todas las detecciones cercanas entre sí.
    """
    latitud: float
    longitud: float
    total_botellas: int
    num_detecciones: int
    confianza_promedio: float
    etiqueta: str
    ultima_deteccion: datetime
    operador: str


# ===========================================================================
# Archivos (galería)
# ===========================================================================

class ArchivoOut(BaseModel):
    """Metadatos de un archivo multimedia de la galería."""
    id: int
    tipo: str
    url: str
    nombre_archivo: Optional[str] = None
    tamanio_bytes: Optional[int] = None
    fecha_captura: datetime
    vuelo_id: Optional[int] = None
    nombre_vuelo: Optional[str] = None
    deteccion_id: Optional[int] = None
    operador: Optional[str] = None

    class Config():
        from_attributes = True


# Resolver referencias circulares (VueloDetalle ↔ DeteccionOut)
VueloDetalle.model_rebuild()