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
    make \
    libxml2-dev \
    libxslt-dev

# Establecer el directorio de trabajo
WORKDIR /app  # Asegúrate de estar en /app

# Copiar todos los archivos del proyecto al contenedor
COPY . /app/

# Limpiar caché de pip y actualizar pip
RUN pip cache purge && \
    pip install --upgrade pip setuptools wheel

# Instalar las dependencias directamente (sin entorno virtual)
RUN pip install -r requirements.txt

# Verificar que Flask se haya instalado correctamente
RUN pip show Flask

# Exponer el puerto (asegurarse de que esté disponible en Railway)
EXPOSE $PORT

# Comando para ejecutar la app con Gunicorn y gevent, asegurándonos de que se use el entorno virtual
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app", "--worker-class", "gevent"]
