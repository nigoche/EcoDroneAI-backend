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
