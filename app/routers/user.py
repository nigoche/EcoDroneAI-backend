from fastapi import APIRouter, Depends
from app.schemas import Usuario, IdUsuario, InfoUsuario
from datetime import datetime
from app.db.database import obtener_bd
from sqlalchemy.orm import Session
from app.db import models
from typing import List

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

usuarios = []

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
        apellido = usuario["apellido"],
        direccion = usuario["direccion"],
        telefono = usuario["telefono"],
        correo = usuario["correo"],
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"respuesta": "Usuario creado con éxito"}

# Forma para obtener un usuario por id usando un path parameter
# ------------------------------------------------------------------------------------------------
# Esta forma funciona tanto con el método 'GET' como con el método 'POST'
@router.get("/id/{id_usuario}", response_model=InfoUsuario)
def obtener_usuario_por_id_en_url(id_usuario:int, db:Session = Depends(obtener_bd)):
    info_usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario).first()
    if not info_usuario:
        return {"respuesta": "Usuario no encontrado"}
    return info_usuario

# Otra forma para obtener un usuario por id sin usar un path parameter, sino un body parameter
# ------------------------------------------------------------------------------------------------
# Este endpoint no funcionará si existe el endpoint anterior, ya que ambos tienen la misma ruta al
# inicio (/usuarios) y FastAPI no sabrá a cuál de los dos endpoints dirigirse cuando se haga una
# petición a esa ruta, ya que una espera por un número en la ruta y la otra espera por un JSON en
# el body, lo que generará un conflicto
#
# Para solucionar esto, se puede cambiar la ruta del endpoint anterior a algo como
# "/usuarios/id/{id_usuario}" o eliminarlo completamente
# ------------------------------------------------------------------------------------------------
# Esta forma no admite el método 'GET' porque no se puede pasar un body en la petición
@router.post("/info")
def obtener_usuario_por_id_en_json(id_usuario:IdUsuario):
    for user in usuarios:
       if user["id"] == id_usuario.valor:
           return {"usuario": user}
    return {"respuesta": "Usuario no encontrado"}

@router.delete("/id/{id_usuario}")
def eliminar_usuario(id_usuario:int):
    for i, usuario in enumerate(usuarios):
        if usuario["id"] == id_usuario:
            usuarios.pop(i)
            return {"respuesta": "Usuario eliminado con éxito"}
    return {"respuesta": "Usuario no encontrado"}

@router.put("/id/{id_usuario}")
def editar_nombre_de_usuario(id_usuario:int, nuevo_usuario:Usuario):
    for i, usuario in enumerate(usuarios):
        if usuario["id"] == id_usuario:
            usuarios[i]["id"] = nuevo_usuario.model_dump()["id"]
            usuarios[i]["nombre"] = nuevo_usuario.model_dump()["nombre"]
            usuarios[i]["apellido"] = nuevo_usuario.model_dump()["apellido"]
            usuarios[i]["direccion"] = nuevo_usuario.model_dump()["direccion"]
            usuarios[i]["telefono"] = nuevo_usuario.model_dump()["telefono"]
            return {"respuesta": "Usuario editado con éxito"}
    return {"respuesta": "Usuario no encontrado"}