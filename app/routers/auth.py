from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import obtener_bd
from app.db import models
from app.schemas import LoginRequest, TokenResponse, RecuperarPasswordRequest
from app.core.security import (
    verificar_password,
    hashear_password,
    crear_access_token,
    obtener_usuario_actual,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)

@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(credenciales: LoginRequest, db: Session = Depends(obtener_bd)):
    """
    Autentica a un usuario con su `username` y `password`

    - Si las credenciales son correctas devuelve un **JWT Bearer** válido por
      `{ACCESS_TOKEN_EXPIRE_MINUTES}` minutos
    - Si son incorrectas responde con **401 Unauthorized**
    """
    # Buscar al usuario en la BD
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.username == credenciales.username)
        .first()
    )

    # Verificación de credenciales con bcrypt (contraseñas hasheadas)
    credenciales_invalidas = not usuario or not verificar_password(
        credenciales.password, usuario.password
    )

    if credenciales_invalidas:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar token JWT
    access_token = crear_access_token(
        data={"sub": usuario.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(access_token=access_token)

@router.post("/logout", summary="Cerrar sesión")
def logout(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """
    Cierra la sesión del usuario autenticado

    > **Nota:** Los JWT son *stateless*, el servidor no puede invalidar tokens emitidos
    > El cliente debe eliminar el token de su almacenamiento local
    """
    return {
        "respuesta": f"Sesión de '{usuario_actual['username']}' cerrada con éxito",
        "instruccion": "Elimina el token de tu almacenamiento local",
    }

@router.post("/recuperar-password", summary="Recuperar contraseña (próximamente)")
def recuperar_password(solicitud: RecuperarPasswordRequest):
    """
    **[DUMMY — En desarrollo]**

    Endpoint de recuperación de contraseña por correo electrónico.
    Actualmente siempre responde con 200 OK para establecer la comunicación
    con el frontend. La funcionalidad real (envío de email con enlace de
    restablecimiento) se implementará en una fase posterior.

    > Requiere integración con un servicio de correo (SMTP / SendGrid / Resend).
    """
    return {
        "respuesta": "Si el correo está registrado, recibirás un enlace de recuperación",
        "correo": solicitud.correo,
        "estado": "pendiente_implementacion",
        "nota": "La funcionalidad de envío de email aún no está activa",
    }