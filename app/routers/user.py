from fastapi import APIRouter
from app.schemas import Usuario, IdUsuario
from datetime import datetime

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

# Lista de usuarios de prueba
usuarios = [
    {"id": 1, "nombre": "Juan", "apellido": "Perez", "direccion": "Calle equis", "telefono": 123456789, "antiguedad": datetime.now()},
    {"id": 2, "nombre": "Pedro", "apellido": "Martínez", "direccion": "Otra calle", "telefono": 987654321, "antiguedad": datetime.now()},
    {"id": 3, "nombre": "Carlos", "apellido": "González", "direccion": "Calle tal", "telefono": 555555555, "antiguedad": datetime.now()},
]

@router.get("/ruta1")
def ruta1():
    return {"mensaje": "Ruta de prueba en mi primera api"}

@router.get("")
def obtener_usuarios():
    return usuarios

@router.post("")
def crear_usuario(user:Usuario):
    usuario = user.model_dump()
    usuarios.append(usuario)
    return {"respuesta": "Usuario creado con éxito"}

# Forma para obtener un usuario por id usando un path parameter
# ------------------------------------------------------------------------------------------------
# Esta forma funciona tanto con el método 'GET' como con el método 'POST'
@router.get("/id/{id_usuario}")     # Endpoint corregido
def obtener_usuario_por_id_en_url(id_usuario:int):
    for usuario in usuarios:
       if usuario["id"] == id_usuario:
           return {"usuario": usuario}
    return {"respuesta": "Usuario no encontrado"}

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