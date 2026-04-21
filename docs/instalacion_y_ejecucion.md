# Guía de instalación y ejecución

## Requisitos

- Entorno de Python ≥3.8.x
- FastAPI
- Uvicorn
- Psycopg2
- SQLAlchemy
- Python-jose[cryptography]
- Passlib[bcrypt]

## Instalación

1. Clonar el repositorio
2. Abrir la terminal en el directorio del proyecto
3. Ejecutar `python -m venv venv` para crear un nuevo entorno virtual de Python
4. Ejecutar `pip install -r requirements.txt` para instalar las dependencias en el entorno virtual del proyecto

## Ejecución

- Para ejecutar el proyecto, primero activa el entorno virtual con el comando `venv/Scripts/activate`
- El archivo `main.py` se encarga de iniciar el servidor de la API, por lo que puedes ejecutarlo con el comando:
  ```bash
  python main.py
  ```
- Puedes acceder a la API en `http://localhost:8000/`
- Revisa `http://localhost:8000/docs` para ver la documentación interactiva de la API y los endpoints disponibles

---
*Si surge cualquier error relacionado con la base de datos, asegúrate de que el servicio de PostgreSQL se encuentre activo y accessible*