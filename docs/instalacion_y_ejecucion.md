# Guía de instalación y ejecución

## Requisitos

- Entorno de Python ≥3.8.x
- FastAPI
- Uvicorn
- Psycopg2
- SQLAlchemy
- Python-jose[cryptography]
- Passlib[bcrypt]
- Bcrypt==4.0.1
- Python-dotenv
- Cuenta en [NeonDB](https://neon.tech) con una base de datos PostgreSQL activa

## Instalación

1. Clonar el repositorio
2. Abrir la terminal en el directorio del proyecto
3. Ejecutar `python -m venv venv` para crear un nuevo entorno virtual de Python
4. Ejecutar `pip install -r requirements.txt` para instalar las dependencias en el entorno virtual del proyecto

## Configuración de variables de entorno

El proyecto utiliza un archivo `.env` para gestionar los valores sensibles. Este archivo **no está incluido en el repositorio** por razones de seguridad.

1. Copia el archivo de plantilla incluido en el repositorio:
   ```bash
   cp .env.example .env
   ```
2. Abre el archivo `.env` y rellena los valores reales:
   - `DATABASE_URL` — la cadena de conexión completa a tu base de datos en NeonDB (disponible en el panel de tu proyecto en neon.tech)
   - `SECRET_KEY` — una clave aleatoria para firmar los tokens JWT. Puedes generar una con:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - `ACCESS_TOKEN_EXPIRE_MINUTES` — tiempo de vida del token en minutos (valor sugerido: `30`)

> Si alguna de estas variables no está definida al arrancar la aplicación, el servidor lanzará un error y no iniciará. Esto es intencional para evitar ejecuciones con credenciales vacías o por defecto.

## Ejecución

- Para ejecutar el proyecto, primero activa el entorno virtual con el comando `venv/Scripts/activate`
- El archivo `main.py` se encarga de iniciar el servidor de la API, por lo que puedes ejecutarlo con el comando:
  ```bash
  python main.py
  ```
- Puedes acceder a la API en `http://localhost:8000/`
- Revisa `http://localhost:8000/docs` para ver la documentación interactiva de la API y los endpoints disponibles

## Autenticación

Todos los endpoints de la API requieren autenticación mediante **JWT Bearer token**. Para obtener uno:

1. Realiza una petición `POST /auth/login` con tu `username` y `password` en el cuerpo
2. Copia el valor de `access_token` de la respuesta
3. En cada petición posterior, incluye el token en el header `Authorization: Bearer <token>`

Puedes utilizar la documentación interactiva (`/docs`) para algunas cosas, pero recomiendo mejor utilizar [Postman](https://www.postman.com/downloads/) para pruebas ya que es más comodo de usar.

---
*La base de datos está alojada en NeonDB (PostgreSQL serverless). No se requiere ningún servicio local de PostgreSQL para ejecutar el proyecto.*