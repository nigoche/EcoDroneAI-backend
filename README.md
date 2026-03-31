# Dos formas de ejecutar un servidor de FastAPI

1. Usando 'uvicorn' en la terminal

```bash
uvicorn main:app --reload
```

2. Agregar las líneas de código necesarias en el archivo 'main.py'

```python
from fastapi import FastAPI
import uvicorn
app = FastAPI()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

y luego ejecutar el archivo 'main.py' en la terminal