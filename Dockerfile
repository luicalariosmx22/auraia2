# Usar una imagen base de Python
FROM python:3.10-slim

# Instalar herramientas necesarias para la compilación de paquetes Cython
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libmariadb-dev \
    gcc \
    g++ \
    make

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar todos los archivos del proyecto
COPY . /app/

# Crear y activar un entorno virtual y asegurarse de instalar herramientas necesarias
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Exponer el puerto (asegurarse de que esté disponible en Railway)
EXPOSE $PORT

# Comando para ejecutar la app con Gunicorn
CMD ["/opt/venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app", "--worker-class", "gevent"]
