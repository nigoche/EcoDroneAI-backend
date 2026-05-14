"""
Router de detecciones.
Registra y consulta las detecciones de botellas PET realizadas por el modelo YOLO v8.
Incluye endpoint especial para el mapa que agrupa puntos cercanos.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import obtener_bd
from app.db import models
from app.schemas import DeteccionCreate, DeteccionOut, PuntoMapa
from app.core.security import obtener_usuario_actual

router = APIRouter(
    prefix="/detecciones",
    tags=["Detecciones"],
)


def _deteccion_a_dict(d: models.Deteccion, db: Session) -> dict:
    """Construye el diccionario de salida de una detección con datos del vuelo."""
    vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == d.vuelo_id).first()
    operador_username = "desconocido"
    if d.operador:
        operador_username = d.operador.username
    elif vuelo and vuelo.operador:
        operador_username = vuelo.operador.username

    return {
        "id": d.id,
        "vuelo_id": d.vuelo_id,
        "nombre_vuelo": vuelo.nombre if vuelo else "sin vuelo",
        "operador": operador_username,
        "timestamp": d.timestamp,
        "latitud": d.latitud,
        "longitud": d.longitud,
        "cantidad_botellas": d.cantidad_botellas,
        "confianza": d.confianza,
        "etiqueta": d.etiqueta,
    }


@router.get("", response_model=List[DeteccionOut], summary="Listar todas las detecciones")
def listar_detecciones(
    vuelo_id: Optional[int] = None,
    etiqueta: Optional[str] = None,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Devuelve todas las detecciones de todos los operadores, ordenadas por timestamp desc.
    Filtros opcionales:
    - `vuelo_id`: solo detecciones de ese vuelo
    - `etiqueta`: filtrar por tipo de desecho (PET, Vidrio, Lata, etc.)
    """
    q = db.query(models.Deteccion)
    if vuelo_id:
        q = q.filter(models.Deteccion.vuelo_id == vuelo_id)
    if etiqueta:
        q = q.filter(models.Deteccion.etiqueta == etiqueta)

    detecciones = q.order_by(models.Deteccion.timestamp.desc()).all()
    return [_deteccion_a_dict(d, db) for d in detecciones]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Registrar detecciones (batch YOLO)")
def registrar_detecciones(
    datos: DeteccionCreate,
    db: Session = Depends(obtener_bd),
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Registra un batch de detecciones provenientes del modelo YOLO v8.
    Acepta una lista de detecciones asociadas a un mismo vuelo.

    El payload esperado es:
    ```json
    {
      "vuelo_id": 3,
      "detecciones": [
        { "timestamp": "...", "latitud": 19.43, "longitud": -99.13,
          "cantidad_botellas": 3, "confianza": 0.87, "etiqueta": "PET" }
      ]
    }
    ```
    """
    # Verificar que el vuelo existe
    vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == datos.vuelo_id).first()
    if not vuelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")

    # Obtener el id del operador desde el JWT
    operador = (
        db.query(models.Usuario)
        .filter(models.Usuario.username == usuario_actual["username"])
        .first()
    )

    nuevas = []
    for item in datos.detecciones:
        det = models.Deteccion(
            vuelo_id=datos.vuelo_id,
            operador_id=operador.id if operador else None,
            timestamp=item.timestamp,
            latitud=item.latitud,
            longitud=item.longitud,
            cantidad_botellas=item.cantidad_botellas,
            confianza=item.confianza,
            etiqueta=item.etiqueta,
        )
        db.add(det)
        nuevas.append(det)

    db.commit()
    return {
        "respuesta": f"{len(nuevas)} detección(es) registrada(s) con éxito",
        "vuelo_id": datos.vuelo_id,
        "total_registradas": len(nuevas),
    }


@router.get("/mapa", response_model=List[PuntoMapa], summary="Puntos agrupados para el mapa")
def obtener_puntos_mapa(
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """
    Devuelve los puntos de detección agrupados por proximidad geográfica
    para mostrar en el mapa interactivo.

    El agrupamiento usa redondeo a 3 decimales (~111 metros de precisión),
    suficiente para clustering visual en un mapa de ciudad.
    """
    detecciones = db.query(models.Deteccion).all()

    # Agrupar por (lat redondeada, lon redondeada, etiqueta)
    grupos: dict = {}
    for d in detecciones:
        lat_r = round(d.latitud, 3)
        lon_r = round(d.longitud, 3)
        clave = (lat_r, lon_r, d.etiqueta)

        if clave not in grupos:
            vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == d.vuelo_id).first()
            operador_name = "desconocido"
            if d.operador:
                operador_name = d.operador.username
            elif vuelo and vuelo.operador:
                operador_name = vuelo.operador.username

            grupos[clave] = {
                "latitud": lat_r,
                "longitud": lon_r,
                "total_botellas": 0,
                "num_detecciones": 0,
                "confianzas": [],
                "etiqueta": d.etiqueta,
                "ultima_deteccion": d.timestamp,
                "operador": operador_name,
            }

        grupos[clave]["total_botellas"] += d.cantidad_botellas
        grupos[clave]["num_detecciones"] += 1
        grupos[clave]["confianzas"].append(d.confianza)
        if d.timestamp > grupos[clave]["ultima_deteccion"]:
            grupos[clave]["ultima_deteccion"] = d.timestamp

    # Calcular confianza promedio y construir lista de salida
    puntos = []
    for g in grupos.values():
        confianzas = g.pop("confianzas")
        g["confianza_promedio"] = round(sum(confianzas) / len(confianzas), 4) if confianzas else 0.0
        puntos.append(g)

    return puntos


@router.get("/{id_deteccion}", response_model=DeteccionOut, summary="Detalle de una detección")
def obtener_deteccion(
    id_deteccion: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """Devuelve la información detallada de una detección específica."""
    d = db.query(models.Deteccion).filter(models.Deteccion.id == id_deteccion).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detección no encontrada")
    return _deteccion_a_dict(d, db)


@router.delete("/{id_deteccion}", summary="Eliminar detección")
def eliminar_deteccion(
    id_deteccion: int,
    db: Session = Depends(obtener_bd),
    _: dict = Depends(obtener_usuario_actual),
):
    """Elimina una detección específica de la base de datos."""
    det_q = db.query(models.Deteccion).filter(models.Deteccion.id == id_deteccion)
    if not det_q.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detección no encontrada")
    det_q.delete(synchronize_session=False)
    db.commit()
    return {"respuesta": "Detección eliminada con éxito"}
