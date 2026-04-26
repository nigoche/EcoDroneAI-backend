# Notas de desarrollo

Este documento compila notas técnicas, consideraciones y aprendizajes obtenidos durante el desarrollo de la API

## Rutas y parámetros

- **Path Parameters**: Para obtener un registro específico (por ejemplo, un usuario por su ID), se utilizan parámetros de ruta en FastAPI. La sintaxis en el decorador es `"/ruta/{id}"`, y la función manejadora lo recibe como un argumento tipado `def funcion(id: int)`
- Esto funciona independientemente del método HTTP (`GET`, `POST`, `PATCH`, `DELETE`)

## Validación de datos

- Para recibir cuerpos de solicitud (Body) se utilizan modelos Pydantic definidos en `schemas.py`. FastAPI se encarga de validar automáticamente que los datos recibidos coincidan con la estructura esperada y generar errores 422 (Unprocessable Entity) en caso contrario

## Autenticación

- Actualmente el proyecto implementa un esquema de autenticación basado en JWT (JSON Web Tokens) a través de `OAuth2PasswordBearer`
- **Nota técnica**: Los JWT son *stateless*, es decir, el servidor no puede invalidar explícitamente tokens que ya han sido emitidos antes de su fecha de expiración. El "cierre de sesión" debe ser manejado en el cliente eliminando el token de su almacenamiento local

## Manejo de errores y excepciones

- **Uso de HTTPException**: Al reportar errores al cliente (como un recurso no encontrado), la buena práctica en FastAPI es lanzar una excepción `HTTPException` (por ejemplo, `raise HTTPException(status_code=404, detail="Usuario no encontrado")`) en lugar de retornar un diccionario convencional
- **Evitar conflictos con `response_model`**: Si un endpoint define un esquema en `response_model`, devolver un diccionario de error en vez de lanzar una excepción provocará que FastAPI intente validar ese error contra el modelo definido. Al no coincidir, generará internamente un error de validación (500 Internal Server Error). Las excepciones evitan este paso de validación y garantizan que se devuelva el código de estado HTTP correcto

## Variables de entorno y ofuscación de datos sensibles

- **El problema del hardcoding**: Escribir credenciales directamente en el código fuente (cadena de conexión a la BD, claves secretas, API keys) es una vulnerabilidad crítica. Cualquier persona con acceso al repositorio obtiene acceso inmediato a los sistemas de producción
- **Solución: archivos `.env`**: Las credenciales se guardan en un archivo `.env` en la raíz del proyecto. Este archivo es ignorado por Git mediante `.gitignore` y **nunca** se sube al repositorio. Solo existe localmente en cada entorno (desarrollo, producción)
- **`python-dotenv`**: La librería `python-dotenv` permite cargar las variables del `.env` al entorno del proceso con `load_dotenv()`. Después se leen con `os.getenv("NOMBRE_VARIABLE")`. Si la variable no existe, la aplicación debe fallar explícitamente con un `RuntimeError` en lugar de usar un valor por defecto inseguro
- **`.env.example`**: Se incluye en el repositorio un archivo `.env.example` con los nombres de todas las variables necesarias pero sin valores reales. Sirve como plantilla para que otros desarrolladores configuren su propio `.env` sin exponer información sensible
- **Fallo explícito en arranque**: En lugar de tener un valor por defecto inseguro (`os.getenv("SECRET_KEY", "clave_debil")`), la buena práctica es levantar un error en el arranque si la variable no está definida. Esto evita que la aplicación corra en producción con credenciales de prueba por un descuido
- **Generación de claves seguras**: Para la `SECRET_KEY` de JWT, se genera una clave aleatoria de 64 caracteres hexadecimales con `python -c "import secrets; print(secrets.token_hex(32))"`. Nunca debe ser una cadena fija ni predecible

## Integración de NeonDB (PostgreSQL en la nube)

- **NeonDB como servicio gestionado**: NeonDB es un servicio de PostgreSQL serverless en la nube. Elimina la necesidad de mantener un servidor de base de datos local o propio, ofreciendo una URL de conexión directa compatible con SQLAlchemy sin cambios en el código de la aplicación
- **Cadena de conexión**: La URL sigue el formato estándar de PostgreSQL: `postgresql://usuario:contraseña@host/nombre_bd?sslmode=require`. Los parámetros `sslmode=require` y `channel_binding=require` son obligatorios para la conexión segura que exige NeonDB
- **`pool_pre_ping=True`**: Al crear el engine de SQLAlchemy se usa esta opción para que antes de cada operación se verifique que la conexión sigue activa. Esto es especialmente importante en servicios serverless donde la conexión puede cerrarse por inactividad

## Protección de endpoints y autenticación

- **Dependencias de FastAPI (`Depends`)**: FastAPI permite declarar funciones de dependencia que se ejecutan antes de cada endpoint. Para proteger rutas con autenticación basta con añadir `_: dict = Depends(obtener_usuario_actual)` como parámetro; si el token es inválido o está ausente, FastAPI responde automáticamente con `401 Unauthorized` antes de ejecutar la lógica del endpoint
- **Endpoints públicos vs protegidos**: No todos los endpoints deben requerir autenticación. La regla general es proteger cualquier operación que lea datos privados, modifique o elimine recursos. Exponer un `GET /usuarios` sin autenticación filtra información de todos los usuarios registrados aunque no devuelva contraseñas
- **Hashing de contraseñas con bcrypt**: Las contraseñas nunca deben almacenarse en texto plano. `passlib` con el esquema `bcrypt` genera un hash irreversible de 60 caracteres. En el login, `verificar_password(plano, hash)` compara sin necesidad de descifrar. La columna de la BD debe tener al menos `VARCHAR(72)` (límite de bcrypt)
- **Compatibilidad `passlib` / `bcrypt`**: `passlib` es incompatible con versiones de `bcrypt >= 5.0` debido a la eliminación del atributo `__about__` en esa versión. La solución es anclar `bcrypt==4.0.1` en `requirements.txt`