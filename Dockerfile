# Usar una imagen base de Python
FROM python:3.10-slim  # [1] Usamos una imagen base ligera de Python 3.10

# Instalar herramientas necesarias para la compilación de paquetes Cython
# y otras dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \  # Herramientas esenciales para compilar software
    python3-dev \    # Headers de Python para compilar extensiones
    libpq-dev \      # Dependencias para PostgreSQL
    libffi-dev \     # Dependencias para libffi
    libssl-dev \     # Dependencias para SSL
    libmariadb-dev \ # Dependencias para MariaDB
    gcc \            # Compilador de C
    g++ \            # Compilador de C++
    make \           # Herramienta de construcción
    libxml2-dev \    # Dependencias para libxml2
    libxslt-dev      # Dependencias para libxslt

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app       # [2] Establecemos /app como el directorio principal

# Copiar todos los archivos del proyecto al contenedor
COPY . /app/       # [3] Copiamos el contenido del directorio local a /app

# Limpiar la caché de pip y actualizar pip, setuptools y wheel
RUN pip cache purge && \
    pip install --upgrade pip setuptools wheel  # [4] Mejoramos las herramientas de empaquetado

# Crear y activar un entorno virtual
RUN python3 -m venv /opt/venv  # [5] Creamos un entorno virtual en /opt/venv
# Modificamos el PATH para usar el entorno virtual
ENV PATH="/opt/venv/bin:$PATH"   # [6]

# Instalar las dependencias de Python desde requirements.txt
RUN /opt/venv/bin/pip install -r requirements.txt  # [7] Instalamos los paquetes en el entorno virtual

# Verificar que Flask se haya instalado correctamente (opcional)
RUN /opt/venv/bin/pip show Flask  # [8] Verificamos la instalación de Flask

# Exponer el puerto que la aplicación escuchará
EXPOSE $PORT      # [9] Exponemos el puerto para que Railway pueda acceder

# Comando para ejecutar la aplicación con Gunicorn y gevent
CMD ["/opt/venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app", "--worker-class", "gevent"]  # [10] Ejecutamos Gunicorn dentro del entorno virtual