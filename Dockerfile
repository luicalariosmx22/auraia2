FROM python:3.10-slim

WORKDIR /app

# 1. Instala dependencias del sistema esenciales
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Instala pip y herramientas básicas
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir wheel setuptools

# 3. Instala PyTorch CPU (previamente, antes de lo demás para evitar conflictos)
RUN pip install --no-cache-dir \
    torch==2.2.2+cpu \
    torchvision==0.17.2+cpu \
    torchaudio==2.2.2+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# 4. Instala el resto de las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todo el código de la app
COPY . .

# 6. Comando de arranque CORREGIDO (expande $PORT correctamente)
CMD gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT
