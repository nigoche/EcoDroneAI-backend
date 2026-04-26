from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import Usuario, InfoUsuario, ActualizarUsuario
from app.db.database import obtener_bd
from sqlalchemy.orm import Session
from app.db import models
from app.core.security import hashear_password, obtener_usuario_actual
from typing import List

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

@router.get("", response_model=List[InfoUsuario], summary="Obtener todos los usuarios")
def obtener_usuarios(
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Recupera una lista con la información básica de todos los usuarios registrados

    Requiere autenticación mediante JWT Bearer
    """
    lista_usuarios = db.query(models.Usuario).all()
    return lista_usuarios

@router.post("", summary="Crear un usuario")
def crear_usuario(
    user: Usuario,
    db: Session = Depends(obtener_bd),
):
    """
    Crea un nuevo usuario en la base de datos a partir de los datos proporcionados

    Espera los campos: username, password, nombre, telefono y correo
    La contraseña es hasheada con bcrypt antes de ser almacenada
    """
    usuario = user.model_dump()
    nuevo_usuario = models.Usuario(
        username=usuario["username"],
        password=hashear_password(usuario["password"]),
        nombre=usuario["nombre"],
        telefono=usuario["telefono"],
        correo=usuario["correo"],
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Usuario creado con éxito")

@router.get("/id/{id_usuario}", response_model=InfoUsuario, summary="Obtener un usuario por id")
def obtener_usuario_por_id(
    id_usuario: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Recupera la información de un usuario en específico filtrando por su ID

    - **id_usuario**: El identificador único del usuario

    Requiere autenticación mediante JWT Bearer
    """
    info_usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario).first()
    if not info_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return info_usuario

@router.delete("/id/{id_usuario}", summary="Eliminar un usuario por id")
def eliminar_usuario(
    id_usuario: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Elimina permanentemente un usuario de la base de datos buscando por su ID

    Requiere autenticación mediante JWT Bearer
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario)
    if not usuario.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    usuario.delete(synchronize_session=False)
    db.commit()
    return {"respuesta": "Usuario eliminado con éxito"}

@router.patch("/id/{id_usuario}", summary="Editar un usuario por id")
def editar_usuario(
    id_usuario: int,
    nuevos_datos: ActualizarUsuario,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Actualiza parcialmente los datos de un usuario existente

    Solo se modificarán los campos que se proporcionen en el cuerpo de la solicitud
    Si se incluye `password`, será hasheada con bcrypt antes de guardarse

    Requiere autenticación mediante JWT Bearer
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario)
    if not usuario.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    datos = nuevos_datos.model_dump(exclude_unset=True)
    # Si se está actualizando la contraseña, hashearla antes de guardar
    if "password" in datos:
        datos["password"] = hashear_password(datos["password"])

    usuario.update(datos)
    db.commit()
    return {"respuesta": "Usuario editado con éxito"}