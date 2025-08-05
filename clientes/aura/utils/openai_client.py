import os
import logging
import json
import time
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv

# Importar librerías necesarias y mantener las existentes
from clientes.aura.logger import logger

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Detectar versión de OpenAI y configurar cliente
import openai
import pkg_resources

# Verificar versión instalada de OpenAI
try:
    openai_version = pkg_resources.get_distribution("openai").version
    logger.info(f"Versión de OpenAI detectada: {openai_version}")
    is_new_version = openai_version.startswith(("1.", "2."))
except Exception as e:
    logger.warning(f"No se pudo determinar la versión de OpenAI: {e}")
    is_new_version = False

def get_openai_client():
    """
    Obtiene un cliente configurado de la API de OpenAI utilizando la clave de API
    almacenada en las variables de entorno.
    
    Returns:
        Union[OpenAI, Any]: Cliente configurado de OpenAI, o None si no se pudo inicializar
    """
    try:
        # Obtener clave de API desde variables de entorno
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Verificar que la clave exista
        if not api_key:
            logger.warning("No se encontró OPENAI_API_KEY en las variables de entorno")
            return None
        
        # Verificar la versión y configurar el cliente apropiadamente
        if is_new_version:
            # Para OpenAI v1.0.0+
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                logger.debug("Cliente OpenAI v1+ inicializado correctamente")
                return client
            except ImportError:
                logger.error("Error al importar OpenAI. La versión detectada puede ser incorrecta.")
                # Fallback a versión anterior
        
        # Para OpenAI v0.x
        openai.api_key = api_key
        logger.debug("Cliente OpenAI v0.x inicializado correctamente")
        return openai
        
    except Exception as e:
        logger.error(f"Error al inicializar cliente de OpenAI: {str(e)}")
        return None

def generar_respuesta(
    prompt: str, 
    model: str = "gpt-3.5-turbo", 
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None
) -> str:
    """
    Genera una respuesta usando la API de OpenAI.
    
    Args:
        prompt (str): Texto de la consulta
        model (str): Modelo a utilizar (default: gpt-3.5-turbo)
        temperature (float): Temperatura para la generación (0.0-1.0)
        max_tokens (int, opcional): Número máximo de tokens en la respuesta
        response_format (Dict, opcional): Formato esperado de la respuesta
        
    Returns:
        str: Texto de la respuesta generada
        
    Raises:
        Exception: Si ocurre un error en la comunicación con la API
    """
    try:
        logger.debug(f"Generando respuesta con modelo {model}, temperatura {temperature}")
        
        # Configurar parámetros de la petición
        params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        # Añadir parámetros opcionales si se proporcionan
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if response_format and "gpt-4" in model:
            # Solo los modelos más nuevos soportan formato de respuesta
            params["response_format"] = response_format
        
        # Obtener cliente adecuado según versión
        client = get_openai_client()
        if not client:
            return "Error: No se pudo inicializar el cliente de OpenAI"
        
        # Realizar la llamada a la API con reintentos
        max_intentos = 3
        espera_base = 2  # segundos
        
        for intento in range(max_intentos):
            try:
                if is_new_version:
                    # Para OpenAI v1.0.0+
                    respuesta = client.chat.completions.create(**params)
                    contenido = respuesta.choices[0].message.content
                else:
                    # Para OpenAI v0.x
                    respuesta = client.ChatCompletion.create(**params)
                    contenido = respuesta.choices[0].message.content
                
                logger.debug(f"Respuesta generada exitosamente: {len(contenido)} caracteres")
                return contenido
                
            except Exception as e:
                if intento < max_intentos - 1:
                    # Espera exponencial antes de reintentar
                    tiempo_espera = espera_base * (2 ** intento)
                    logger.warning(f"Error en intento {intento+1}/{max_intentos}: {str(e)}. Reintentando en {tiempo_espera}s")
                    time.sleep(tiempo_espera)
                else:
                    # Último intento fallido, propagar el error
                    raise
        
    except Exception as e:
        logger.error(f"Error al generar respuesta: {str(e)}")
        # Devolver un mensaje de error formateado en caso de fallo
        return f"Error al procesar la solicitud: {str(e)}"

def generar_embeddings(texto: str) -> List[float]:
    """
    Genera embeddings (representación vectorial) de un texto usando la API de OpenAI.
    
    Args:
        texto (str): Texto para generar embeddings
        
    Returns:
        List[float]: Vector de embeddings
        
    Raises:
        Exception: Si ocurre un error en la comunicación con la API
    """
    try:
        client = get_openai_client()
        if not client:
            raise Exception("No se pudo inicializar el cliente de OpenAI")
            
        if is_new_version:
            # Para OpenAI v1.0.0+
            respuesta = client.embeddings.create(
                input=texto,
                model="text-embedding-ada-002"
            )
            embeddings = respuesta.data[0].embedding
        else:
            # Para OpenAI v0.x
            respuesta = client.Embedding.create(
                input=texto,
                model="text-embedding-ada-002"
            )
            embeddings = respuesta.data[0].embedding
            
        logger.debug(f"Embeddings generados correctamente: {len(embeddings)} dimensiones")
        return embeddings
    
    except Exception as e:
        logger.error(f"Error al generar embeddings: {str(e)}")
        raise