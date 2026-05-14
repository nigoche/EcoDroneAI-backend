"""
seeder.py -- Script de datos de prueba para EcoDrone AI

Genera datos simulados realistas para probar el frontend sin necesidad
de tener el modelo YOLO v8 funcionando.

Genera:
  - 2 operadores de prueba
  - 5 vuelos por operador (10 vuelos total)
  - 3 a 15 detecciones por vuelo (~80 detecciones total)
  - URLs de imagenes de stock para la galeria (Unsplash, libres)

Uso:
  python seeder.py

El script es idempotente: si ya existen los operadores de prueba,
no los duplica, solo agrega vuelos y detecciones nuevas.
"""

import random
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.db.models import Usuario, Vuelo, Deteccion, Archivo
from app.core.security import hashear_password

# ---------------------------------------------------------------------------
# Configuracion de datos de prueba
# ---------------------------------------------------------------------------

OPERADORES_SEED = [
    {"username": "juan_ops", "correo": "juan@ecodrone.test", "password": "test1234"},
    {"username": "ana_ops",  "correo": "ana@ecodrone.test",  "password": "test1234"},
]

# Coordenadas base: Ciudad de Mexico (zonas reales)
ZONAS = [
    {"nombre": "Parque Bicentenario",  "lat": 19.4538, "lon": -99.1949},
    {"nombre": "Canal de Chalco",      "lat": 19.2780, "lon": -98.9010},
    {"nombre": "Cerro de la Estrella", "lat": 19.3523, "lon": -99.0889},
    {"nombre": "Xochimilco",           "lat": 19.2595, "lon": -99.1062},
    {"nombre": "Barranca del Muerto",  "lat": 19.3697, "lon": -99.1977},
]

# Imagenes de muestra de botellas PET (Unsplash -- libres para uso)
IMAGENES_STOCK = [
    "https://images.unsplash.com/photo-1527515862778-d1b6e0d12e64?w=800",
    "https://images.unsplash.com/photo-1604187351574-c75ca79f5807?w=800",
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
    "https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800",
    "https://images.unsplash.com/photo-1591193686104-fddba7237a5c?w=800",
    "https://images.unsplash.com/photo-1572362912132-288a1781e697?w=800",
    "https://images.unsplash.com/photo-1603123853880-a92fec8cff3a?w=800",
    "https://images.unsplash.com/photo-1484417894907-623942c8ee29?w=800",
]

ETIQUETAS = ["PET", "PET", "PET", "Vidrio", "Lata"]  # PET mas frecuente


def offset_coord(base: float, magnitud: float = 0.02) -> float:
    """Aplica un desplazamiento aleatorio pequeno a una coordenada."""
    return round(base + random.uniform(-magnitud, magnitud), 6)


def fecha_aleatoria(dias_atras: int = 30) -> datetime:
    """Devuelve un datetime aleatorio en los ultimos N dias."""
    ahora = datetime.utcnow()
    delta = timedelta(
        days=random.randint(0, dias_atras),
        hours=random.randint(6, 18),
        minutes=random.randint(0, 59),
    )
    return ahora - delta


def main():
    db = SessionLocal()
    try:
        print("=" * 55)
        print("  EcoDrone AI -- Seeder de datos de prueba")
        print("=" * 55)

        # ----------------------------------------------------------------
        # 1. Crear operadores de prueba
        # ----------------------------------------------------------------
        operadores = []
        for datos in OPERADORES_SEED:
            existente = db.query(Usuario).filter(
                Usuario.username == datos["username"]
            ).first()
            if existente:
                print(f"  [OK] Operador ya existe: @{datos['username']}")
                operadores.append(existente)
            else:
                nuevo = Usuario(
                    username=datos["username"],
                    correo=datos["correo"],
                    password=hashear_password(datos["password"]),
                )
                db.add(nuevo)
                db.commit()
                db.refresh(nuevo)
                operadores.append(nuevo)
                print(f"  [+] Operador creado: @{datos['username']} (password: {datos['password']})")

        # ----------------------------------------------------------------
        # 2. Crear vuelos
        # ----------------------------------------------------------------
        print("\n  Generando vuelos y detecciones...\n")
        total_vuelos = 0
        total_detecciones = 0
        total_archivos = 0

        for operador in operadores:
            for i in range(5):
                zona = random.choice(ZONAS)
                fecha_ini = fecha_aleatoria(dias_atras=30)
                duracion = timedelta(minutes=random.randint(20, 75))
                num_det = random.randint(3, 15)

                vuelo = Vuelo(
                    operador_id=operador.id,
                    nombre=f"Vuelo {zona['nombre']} #{i+1}",
                    fecha_inicio=fecha_ini,
                    fecha_fin=fecha_ini + duracion,
                    latitud_inicio=zona["lat"],
                    longitud_inicio=zona["lon"],
                    notas=f"Vuelo de prueba. Zona: {zona['nombre']}.",
                    sincronizado=random.choice([True, False]),
                )
                db.add(vuelo)
                db.commit()
                db.refresh(vuelo)
                total_vuelos += 1

                # --------------------------------------------------------
                # 3. Crear detecciones del vuelo (simula salida YOLO)
                # --------------------------------------------------------
                for j in range(num_det):
                    ts = fecha_ini + timedelta(
                        seconds=random.randint(30, int(duracion.total_seconds() - 30))
                    )
                    det = Deteccion(
                        vuelo_id=vuelo.id,
                        operador_id=operador.id,
                        timestamp=ts,
                        latitud=offset_coord(zona["lat"]),
                        longitud=offset_coord(zona["lon"]),
                        cantidad_botellas=random.randint(1, 8),
                        confianza=round(random.uniform(0.55, 0.98), 4),
                        etiqueta=random.choice(ETIQUETAS),
                    )
                    db.add(det)
                    db.commit()
                    db.refresh(det)
                    total_detecciones += 1

                    # --------------------------------------------------------
                    # 4. Crear archivos (imagen de stock) para cada deteccion
                    # --------------------------------------------------------
                    num_archivos = random.randint(1, 2)
                    for _ in range(num_archivos):
                        arch = Archivo(
                            vuelo_id=vuelo.id,
                            deteccion_id=det.id,
                            operador_id=operador.id,
                            tipo="imagen",
                            url=random.choice(IMAGENES_STOCK),
                            nombre_archivo=f"frame_{vuelo.id}_{det.id}_{j}.jpg",
                            tamanio_bytes=random.randint(200_000, 2_000_000),
                            fecha_captura=ts,
                        )
                        db.add(arch)
                        total_archivos += 1

                db.commit()
                print(f"  [+] '{vuelo.nombre}' ({num_det} detecciones) -- @{operador.username}")

        # ----------------------------------------------------------------
        # Resumen
        # ----------------------------------------------------------------
        print("\n" + "=" * 55)
        print("  Seeder completado exitosamente:")
        print(f"    Operadores : {len(operadores)}")
        print(f"    Vuelos     : {total_vuelos}")
        print(f"    Detecciones: {total_detecciones}")
        print(f"    Archivos   : {total_archivos}")
        print("=" * 55)
        print("\n  Credenciales de prueba:")
        for op in OPERADORES_SEED:
            print(f"    username: {op['username']}  |  password: {op['password']}")
        print()

    except Exception as e:
        db.rollback()
        print(f"\n  [ERROR] Error durante el seeder: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
