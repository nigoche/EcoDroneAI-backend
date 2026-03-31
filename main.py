from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/ruta1")
def ruta1():
    return {"mensaje": "Ruta de prueba en mi primera api"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)