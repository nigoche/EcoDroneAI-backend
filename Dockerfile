# ─── EcoDroneAI Backend — Dockerfile ─────────────────────────────────────────
# Imagen base oficial de Python (Linux Debian slim, ligera y segura)
FROM python:3.11-slim

# Evita archivos .pyc y asegura salida de logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias del sistema necesarias para psycopg2-binary
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente al contenedor
COPY . .

# Expone el puerto de la API
EXPOSE 8000

# Inicia Uvicorn sin --reload (adecuado para producción/staging)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
