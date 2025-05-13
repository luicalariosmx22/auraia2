# Usar una imagen base de Python
FROM python:3.10-slim

# Instalar herramientas de compilación y dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential python3-dev libpq-dev libffi-dev libssl-dev \
    libmariadb-dev gcc g++ make libxml2-dev libxslt-dev

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app/

# Limpiar caché de pip y actualizar pip
RUN pip cache purge && pip install --upgrade pip setuptools wheel

# Crear y activar entorno virtual
RUN python3 -m venv /opt/venv
# Usar el PATH del entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias de Python
RUN /opt/venv/bin/pip install -r requirements.txt

# Verificar instalación de Flask (opcional)
RUN /opt/venv/bin/pip show Flask

# Exponer el puerto
EXPOSE $PORT

# Ejecutar la aplicación con Gunicorn
CMD ["/opt/venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app", "--worker-class", "gevent"]