from fastapi import APIRouter, Depends
from app.schemas import Usuario, InfoUsuario, ActualizarUsuario
from app.db.database import obtener_bd
from sqlalchemy.orm import Session
from app.db import models
from typing import List

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

@router.get("", response_model=List[InfoUsuario])
def obtener_usuarios(db:Session = Depends(obtener_bd)):
    lista_usuarios = db.query(models.Usuario).all()
    return lista_usuarios

@router.post("")
def crear_usuario(user:Usuario, db:Session = Depends(obtener_bd)):
    usuario = user.model_dump()
    nuevo_usuario = models.Usuario(
        username = usuario["username"],
        password = usuario["password"],
        nombre = usuario["nombre"],
        telefono = usuario["telefono"],
        correo = usuario["correo"],
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"respuesta": "Usuario creado con éxito"}

# Forma para obtener un usuario por id usando un path parameter
# -----------------------------------------------------------------------------------------
# Esta forma funciona tanto con el método 'GET' como con el método 'POST'
@router.get("/id/{id_usuario}", response_model=InfoUsuario)
def obtener_usuario_por_id_en_url(id_usuario:int, db:Session = Depends(obtener_bd)):
    info_usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario).first()
    if not info_usuario:
        return {"respuesta": "Usuario no encontrado"}
    return info_usuario

@router.delete("/id/{id_usuario}")
def eliminar_usuario(id_usuario:int, db:Session = Depends(obtener_bd)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario)
    if not usuario.first():
        return {"respuesta": "Usuario no encontrado"}
    usuario.delete(synchronize_session=False)
    db.commit()
    return {"respuesta": "Usuario eliminado con éxito"}

@router.patch("/id/{id_usuario}")
def editar_nombre_de_usuario(id_usuario:int, nuevos_datos:ActualizarUsuario, db:Session = Depends(obtener_bd)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario)
    if not usuario.first():
        return {"respuesta": "Usuario no encontrado"}
    usuario.update(nuevos_datos.model_dump(exclude_unset=True))
    db.commit()
    return {"respuesta": "Usuario editado con éxito"}