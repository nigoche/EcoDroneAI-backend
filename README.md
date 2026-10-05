# 🛸 EcoDrone AI — Backend & API RESTful

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-NeonDB-336791?style=flat&logo=postgresql&logoColor=white)](https://neon.tech/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-D71F00?style=flat)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT%20Bearer-black?style=flat&logo=jsonwebtokens)](https://jwt.io/)
[![YOLOv8](https://img.shields.io/badge/AI%20Vision-YOLOv8-FF6F00?style=flat)](https://ultralytics.com/)

Servicio backend distribuido y API RESTful de alto rendimiento diseñado para la plataforma **EcoDrone AI**, un sistema de reconocimiento aéreo orientado a la detección, conteo y mapeo geoespacial de residuos plásticos (botellas PET) mediante drones autónomos equipados con visión por computadora.

---

## 📌 Descripción del Proyecto

EcoDrone AI combina vehículos aéreos no tripulados, visión artificial e infraestructura en la nube para automatizar el monitoreo ambiental. Este repositorio contiene el **servidor backend**, responsable de:

1. **Gestión de Seguridad & Autenticación:** Flujo de autenticación OAuth2 con tokens criptográficos JWT y hashing seguro de credenciales con Bcrypt.
2. **Telemetría y Registro de Vuelos:** Registro en tiempo real de sesiones operativas del dron, metadatos de vuelo y coordenadas GPS.
3. **Persistencia de Detecciones:** Almacenamiento estructurado de las detecciones generadas por el modelo de visión artificial (YOLOv8), incluyendo nivel de confianza, coordenadas y marcas de tiempo.
4. **Alimentación al Cliente Móvil:** API para visualización de mapas de calor, estadísticas y galería multimedia en la aplicación móvil de campo (desarrollada en Flutter con OpenStreetMap).

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una arquitectura modular y desacoplada basada en capas de responsabilidad:

```text
EcoDroneAI-backend/
├── app/
│   ├── core/           # Seguridad (JWT, hashing de contraseñas) y configuración global
│   ├── db/             # Conexión al pool de NeonDB y modelos declarativos (SQLAlchemy)
│   ├── routers/        # Controladores de la API (Auth, Vuelos, Detecciones, Multimedia)
│   └── schemas.py      # Validación estricta de esquemas de datos con Pydantic
├── docs/               # Documentación técnica extendida
│   ├── instalacion_y_ejecucion.md
│   ├── estructura_del_proyecto.md
│   ├── notas_de_desarrollo.md
│   └── registro_de_cambios.md
├── main.py             # Instancia principal de FastAPI y configuración de CORS
└── requirements.txt    # Dependencias del ecosistema Python
```

### Stack Tecnológico
* **Lenguaje:** Python 3.10+
* **Framework Web:** FastAPI (asíncrono, alto rendimiento basado en Starlette y Pydantic)
* **Persistencia:** PostgreSQL serverless alojado en [NeonDB](https://neon.tech)
* **ORM:** SQLAlchemy con soporte para transacciones y relaciones foráneas
* **Seguridad:** Tokens JWT (`python-jose`) y hashing Bcrypt (`passlib`)
* **Servidor ASGI:** Uvicorn

---

## 🚀 Inicio Rápido e Instalación

### 1. Prerrequisitos
* Python 3.10 o superior instalado.
* Base de datos activa en NeonDB (o instancia local de PostgreSQL).

### 2. Clonación y entorno virtual
```bash
git clone https://github.com/nigoche/EcoDroneAI-backend.git
cd EcoDroneAI-backend

# Crear entorno virtual
python -m venv venv

# Activar entorno (Linux/macOS)
source venv/bin/activate
# En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de variables de entorno
Crea un archivo `.env` basado en la plantilla de ejemplo:
```bash
cp .env.example .env
```

Configura tus credenciales reales en `.env`:
```env
DATABASE_URL=postgresql://usuario:password@ep-ejemplo.neon.tech/neondb?sslmode=require
SECRET_KEY=tu_clave_secreta_hexadecimal_aleatoria
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Generador de SECRET_KEY rápida:**
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Ejecución del servidor
```bash
python main.py
```
El servidor quedará en ejecución en: `http://localhost:8000`

---

## 📖 Documentación Interactiva de la API

FastAPI genera documentación OpenAPI en tiempo real. Con el servidor en ejecución, accede a:
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) (permite probar endpoints interactivamente con autorización Bearer).
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc) (especificación técnica estructurada).

### Endpoints Principales
| Método | Endpoint | Descripción | Requiere Auth |
| :--- | :--- | :--- | :---: |
| `POST` | `/auth/register` | Registro de nuevos operadores de campo | No |
| `POST` | `/auth/login` | Autenticación y expedición de JWT Bearer token | No |
| `GET` | `/vuelos/` | Historial de sesiones y misiones de vuelo | Sí |
| `POST` | `/vuelos/` | Alta de nueva misión con metadatos de inicio | Sí |
| `GET` | `/detecciones/` | Consulta y filtrado de objetos detectados (PET) | Sí |
| `POST` | `/detecciones/` | Registro de hallazgo de residuos con geolocalización | Sí |

---

## 📚 Documentación Técnica Detallada

Para profundizar en el diseño e implementación del sistema:
* 📖 [Guía detallada de instalación y entorno](docs/instalacion_y_ejecucion.md)
* 🏗️ [Estructura modular del proyecto](docs/estructura_del_proyecto.md)
* 💡 [Notas de arquitectura y decisiones de diseño](docs/notas_de_desarrollo.md)
* 📝 [Registro de versiones y cambios (Changelog)](docs/registro_de_cambios.md)

---

## 👨‍💻 Autor
**Jesús García Nigoche**  
*Estudiante de Ingeniería en Sistemas Computacionales | Desarrollador Backend & Residente Cinvestav*  
* GitHub: [@nigoche](https://github.com/nigoche)
* LinkedIn: [linkedin.com/in/nigoche](https://linkedin.com/in/nigoche)