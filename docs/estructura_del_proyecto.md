# Estructura del proyecto

El proyecto está diseñado con FastAPI, dividiendo responsabilidades en distintos módulos

```text
backend/
├── app/
│   ├── core/           # Configuraciones clave (ej. variables de entorno, seguridad, hashing, tokens)
│   ├── db/             # Conexión a base de datos y definición de modelos (SQLAlchemy)
│   ├── routers/        # Controladores (endpoints) divididos por entidad
│   └── schemas.py      # Modelos de Pydantic para validación de datos de entrada/salida
├── docs/               # Documentación del proyecto en Markdown
├── main.py             # Punto de entrada principal de la aplicación FastAPI
└── requirements.txt    # Dependencias de Python
```

## Descripción de los módulos

- **`app/core/security.py`**: Maneja la generación y validación de tokens JWT, así como el hashing de contraseñas
- **`app/db/database.py`**: Instancia del motor SQLAlchemy y gestión de sesiones de BD
- **`app/db/models.py`**: Define las tablas de la base de datos usando clases declarativas
- **`app/routers/`**: Contiene los `APIRouter` que agrupan las rutas relacionadas para mantener limpio `main.py`
- **`app/schemas.py`**: Define cómo deben lucir los datos que el cliente envía y cómo luce la respuesta de la API
