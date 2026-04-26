import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError(
        "La variable de entorno SECRET_KEY no está definida. "
        "Genera una con: python -c \"import secrets; print(secrets.token_hex(32))\""
    )

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ---------------------------------------------------------------------------
# Hashing de contraseñas
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Compara una contraseña en texto plano con su hash bcrypt"""
    return pwd_context.verify(password_plano, password_hash)

def hashear_password(password: str) -> str:
    """Genera un hash bcrypt para la contraseña dada"""
    return pwd_context.hash(password)

# ---------------------------------------------------------------------------
# JSON Web Tokens
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def crear_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Genera un JWT firmado con la clave secreta
    - data: payload a incluir en el token (p. ej. {"sub": username})
    - expires_delta: tiempo de vida del token; si es None usa el valor por defecto
    """
    payload = data.copy()
    ahora = datetime.now(timezone.utc)
    expira = ahora + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expira, "iat": ahora})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependencia FastAPI: decodifica y valida el JWT del header Authorization
    Devuelve el payload del token o lanza 401 si es inválido/expirado
    """
    credenciales_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credenciales_exc
        return {"username": username}
    except JWTError:
        raise credenciales_exc