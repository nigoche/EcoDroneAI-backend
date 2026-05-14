"""
Router de vuelos.
Permite crear, consultar, actualizar y eliminar registros de vuelo del dron.
Todos los operadores pueden ver todos los vuelos (con información del autor).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app.db.database import obtener_bd
from app.db import models
from app.schemas import VueloCreate, VueloUpdate, VueloOut, VueloDetalle
from app.core.security import obtener_usuario_actual

router = APIRouter(
    prefix="/vuelos",
    tags=["Vuelos"],
)


def _enriquecer_vuelo(vuelo: models.Vuelo, db: Session) -> dict:
    """Agrega campos calculados (num_detecciones, total botellas) a un objeto vuelo."""
    num_detecciones = (
        db.query(func.count(models.Deteccion.id))
        .filter(models.Deteccion.vuelo_id == vuelo.id)
        .scalar() or 0
    )
    num_botellas = (
        db.query(func.sum(models.Deteccion.cantidad_botellas))
        .filter(models.Deteccion.vuelo_id == vuelo.id)
        .scalar() or 0
    )
    return {
        "id": vuelo.id,
        "nombre": vuelo.nombre,
        "fecha_inicio": vuelo.fecha_inicio,
        "fecha_fin": vuelo.fecha_fin,
        "latitud_inicio": vuelo.latitud_inicio,
        "longitud_inicio": vuelo.longitud_inicio,
        "sincronizado": vuelo.sincronizado,
        "operador": vuelo.operador.username if vuelo.operador else "desconocido",
        "num_detecciones": num_detecciones,
        "num_botellas_total": int(num_botellas),
    }


@router.get("", response_model=List[VueloOut], summary="Listar todos los vuelos")
def listar_vuelos(
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Devuelve todos los vuelos registrados por todos los operadores,
    ordenados del más reciente al más antiguo.
    Incluye contadores de detecciones y botellas por vuelo.
    """
    vuelos = (
        db.query(models.Vuelo)
        .order_by(models.Vuelo.fecha_inicio.desc())
        .all()
    )
    return [_enriquecer_vuelo(v, db) for v in vuelos]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=VueloOut, summary="Crear vuelo")
def crear_vuelo(
    datos: VueloCreate,
    db: Session = Depends(obtener_bd),
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Registra un nuevo vuelo de dron.
    El operador_id se extrae automáticamente del JWT del usuario autenticado.
    """
    operador = (
        db.query(models.Usuario)
        .filter(models.Usuario.username == usuario_actual["username"])
        .first()
    )
    if not operador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operador no encontrado")

    nuevo_vuelo = models.Vuelo(
        operador_id=operador.id,
        nombre=datos.nombre,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        latitud_inicio=datos.latitud_inicio,
        longitud_inicio=datos.longitud_inicio,
        notas=datos.notas,
    )
    db.add(nuevo_vuelo)
    db.commit()
    db.refresh(nuevo_vuelo)
    return _enriquecer_vuelo(nuevo_vuelo, db)


@router.get("/{id_vuelo}", response_model=VueloDetalle, summary="Detalle de un vuelo")
def obtener_vuelo(
    id_vuelo: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Devuelve la información completa de un vuelo incluyendo
    todas sus detecciones asociadas.
    """
    vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == id_vuelo).first()
    if not vuelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")

    base = _enriquecer_vuelo(vuelo, db)
    base["notas"] = vuelo.notas

    # Construir lista de detecciones para el detalle
    detecciones_out = []
    for d in vuelo.detecciones:
        detecciones_out.append({
            "id": d.id,
            "vuelo_id": d.vuelo_id,
            "nombre_vuelo": vuelo.nombre,
            "operador": vuelo.operador.username if vuelo.operador else "desconocido",
            "timestamp": d.timestamp,
            "latitud": d.latitud,
            "longitud": d.longitud,
            "cantidad_botellas": d.cantidad_botellas,
            "confianza": d.confianza,
            "etiqueta": d.etiqueta,
        })
    base["detecciones"] = detecciones_out
    return base


@router.patch("/{id_vuelo}", response_model=VueloOut, summary="Actualizar vuelo")
def actualizar_vuelo(
    id_vuelo: int,
    datos: VueloUpdate,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Actualiza parcialmente un vuelo existente.
    Útil para marcar como sincronizado, agregar fecha_fin o notas.
    """
    vuelo_q = db.query(models.Vuelo).filter(models.Vuelo.id == id_vuelo)
    if not vuelo_q.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")

    vuelo_q.update(datos.model_dump(exclude_unset=True))
    db.commit()
    return _enriquecer_vuelo(vuelo_q.first(), db)


@router.delete("/{id_vuelo}", summary="Eliminar vuelo")
def eliminar_vuelo(
    id_vuelo: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Elimina un vuelo y todas sus detecciones y archivos asociados (cascade).
    """
    vuelo_q = db.query(models.Vuelo).filter(models.Vuelo.id == id_vuelo)
    if not vuelo_q.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")

    vuelo_q.delete(synchronize_session=False)
    db.commit()
    return {"respuesta": "Vuelo eliminado con éxito"}
