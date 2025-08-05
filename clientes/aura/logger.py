import logging
import os
from datetime import datetime
import sys

# Configuración del directorio de logs
def _setup_log_directory():
    logs_dir = os.path.join("clientes", "aura", "logs")
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
        except Exception as e:
            print(f"❌ No se pudo crear el directorio de logs: {e}")
            # Fallback a directorio temporal si no se puede crear
            logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
    return logs_dir

# Formato de fecha para los archivos de log
def _get_log_filename():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"aura_{today}.log"

def configure_logger():
    """
    Configura y devuelve el logger principal de la aplicación.
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Configurar logger principal
    logger = logging.getLogger('aura')
    logger.setLevel(logging.DEBUG)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
        
    # Formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Handler para consola
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    try:
        # Handler para archivo
        logs_dir = _setup_log_directory()
        file_handler = logging.FileHandler(
            os.path.join(logs_dir, _get_log_filename()),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"❌ Error al configurar el log en archivo: {e}")
        # Continuar sin log en archivo
    
    return logger

# Instancia global del logger
logger = configure_logger()