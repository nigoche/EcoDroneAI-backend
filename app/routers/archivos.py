"""
Router de archivos multimedia (galería).
Maneja la subida, consulta y eliminación de imágenes y videos de vuelo.

Storage actual: disco local bajo UPLOAD_DIR (configurable vía .env).
Para activar Cloudinary en producción, descomentar las secciones marcadas
y agregar CLOUDINARY_URL al .env.
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import obtener_bd
from app.db import models
from app.schemas import ArchivoOut
from app.core.security import obtener_usuario_actual
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/archivos",
    tags=["Archivos (Galería)"],
)

# ---------------------------------------------------------------------------
# Configuración de storage local
# ---------------------------------------------------------------------------
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

TIPOS_PERMITIDOS = {
    "image/jpeg": ("imagen", ".jpg"),
    "image/png": ("imagen", ".png"),
    "image/webp": ("imagen", ".webp"),
    "video/mp4": ("video", ".mp4"),
    "video/quicktime": ("video", ".mov"),
}

# ---------------------------------------------------------------------------
# Para Cloudinary (PRODUCCIÓN): descomentar y agregar CLOUDINARY_URL al .env
# ---------------------------------------------------------------------------
# import cloudinary
# import cloudinary.uploader
# cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))


def _archivo_a_dict(a: models.Archivo, db: Session) -> dict:
    """Construye el diccionario de salida de un archivo."""
    vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == a.vuelo_id).first() if a.vuelo_id else None
    operador_name = None
    if a.operador:
        operador_name = a.operador.username
    elif vuelo and vuelo.operador:
        operador_name = vuelo.operador.username

    return {
        "id": a.id,
        "tipo": a.tipo.value if hasattr(a.tipo, "value") else a.tipo,
        "url": a.url,
        "nombre_archivo": a.nombre_archivo,
        "tamanio_bytes": a.tamanio_bytes,
        "fecha_captura": a.fecha_captura,
        "vuelo_id": a.vuelo_id,
        "nombre_vuelo": vuelo.nombre if vuelo else None,
        "deteccion_id": a.deteccion_id,
        "operador": operador_name,
    }


@router.get("", response_model=List[ArchivoOut], summary="Listar archivos de la galería")
def listar_archivos(
    vuelo_id: Optional[int] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Devuelve todos los archivos multimedia ordenados por fecha de captura desc.
    Filtros opcionales: `vuelo_id`, `tipo` (imagen | video).
    """
    q = db.query(models.Archivo)
    if vuelo_id:
        q = q.filter(models.Archivo.vuelo_id == vuelo_id)
    if tipo:
        q = q.filter(models.Archivo.tipo == tipo)

    archivos = q.order_by(models.Archivo.fecha_captura.desc()).all()
    return [_archivo_a_dict(a, db) for a in archivos]


@router.post("/subir", status_code=status.HTTP_201_CREATED, response_model=ArchivoOut, summary="Subir imagen o video")
async def subir_archivo(
    archivo: UploadFile = File(...),
    vuelo_id: Optional[int] = Form(None),
    deteccion_id: Optional[int] = Form(None),
    db: Session = Depends(obtener_bd),
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Sube una imagen (JPG, PNG, WebP) o video (MP4, MOV) al servidor.
    
    - El archivo queda disponible en `/uploads/{nombre_unico}`
    - `vuelo_id` y `deteccion_id` son opcionales para vincular el archivo
    
    **Tipos permitidos**: image/jpeg, image/png, image/webp, video/mp4, video/quicktime
    """
    # Validar tipo de archivo
    content_type = archivo.content_type or ""
    if content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido: {content_type}. "
                   f"Permitidos: {', '.join(TIPOS_PERMITIDOS.keys())}",
        )

    tipo_str, extension = TIPOS_PERMITIDOS[content_type]

    # Validar que el vuelo existe si se proporcionó
    if vuelo_id:
        vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == vuelo_id).first()
        if not vuelo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")

    # Obtener operador
    operador = (
        db.query(models.Usuario)
        .filter(models.Usuario.username == usuario_actual["username"])
        .first()
    )

    # -----------------------------------------------------------------------
    # Storage LOCAL (desarrollo)
    # -----------------------------------------------------------------------
    nombre_unico = f"{uuid.uuid4().hex}{extension}"
    ruta_local = UPLOAD_DIR / nombre_unico
    contenido = await archivo.read()
    ruta_local.write_bytes(contenido)
    url_archivo = f"/uploads/{nombre_unico}"
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Storage CLOUDINARY (producción) — descomentar para activar:
    # -----------------------------------------------------------------------
    # resultado = cloudinary.uploader.upload(
    #     contenido,
    #     public_id=nombre_unico,
    #     resource_type="auto",   # auto detecta imagen o video
    # )
    # url_archivo = resultado["secure_url"]
    # -----------------------------------------------------------------------

    nuevo_archivo = models.Archivo(
        vuelo_id=vuelo_id,
        deteccion_id=deteccion_id,
        operador_id=operador.id if operador else None,
        tipo=tipo_str,
        url=url_archivo,
        nombre_archivo=archivo.filename,
        tamanio_bytes=len(contenido),
        fecha_captura=datetime.utcnow(),
    )
    db.add(nuevo_archivo)
    db.commit()
    db.refresh(nuevo_archivo)
    return _archivo_a_dict(nuevo_archivo, db)


@router.get("/{id_archivo}", response_model=ArchivoOut, summary="Metadatos de un archivo")
def obtener_archivo(
    id_archivo: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """Devuelve los metadatos de un archivo específico por su ID."""
    a = db.query(models.Archivo).filter(models.Archivo.id == id_archivo).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")
    return _archivo_a_dict(a, db)


@router.delete("/{id_archivo}", summary="Eliminar archivo")
def eliminar_archivo(
    id_archivo: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Elimina los metadatos del archivo de la BD y, si está en disco local,
    también elimina el fichero físico.
    """
    a = db.query(models.Archivo).filter(models.Archivo.id == id_archivo).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    # Intentar eliminar archivo físico local si existe
    if a.url.startswith("/uploads/"):
        nombre = a.url.replace("/uploads/", "")
        ruta = UPLOAD_DIR / nombre
        if ruta.exists():
            ruta.unlink()

    db.delete(a)
    db.commit()
    return {"respuesta": "Archivo eliminado con éxito"}
