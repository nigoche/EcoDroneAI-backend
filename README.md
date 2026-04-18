# EcoDrone AI Backend by <i>nigoche</i>
(2/abr/26) Etapa 1: endpoints de usuarios
(5/abr/26) Etapa 2: modularización de la API e implementación de los principales métodos HTTP
(8/abr/26) Etapa 3: conexión a la base de datos
(16/abr/26) Etapa 4: refactorización de los endpoints y fin de las pruebas

## Requisitos

- Python 3.8.x
- FastAPI
- Uvicorn
- Psycopg2
- SQLAlchemy

## Instalación

1. Clonar el repositorio
2. Abrir la terminal en el directorio del proyecto
3. Ejecutar `python -m venv venv` para crear un nuevo entorno virtual de Python
4. Ejecutar `pip install -r requirements.txt` para instalar las dependencias en el entorno virtual del proyecto

## Ejecución

- El archivo `main.py` se encarga de iniciar el servidor de la API, por lo que puedes ejecutarlo con el comando `python main.py`
- Puedes acceder a la API en `http://127.0.0.1:8000/`
- Revisa `localhost:8000/docs` para ver la documentación de la API y los endpoints disponibles