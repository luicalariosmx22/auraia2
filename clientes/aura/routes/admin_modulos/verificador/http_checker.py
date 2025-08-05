import os
import time
import json
import requests
from typing import Dict, Any, Union, List, Optional
from requests.exceptions import RequestException, Timeout, ConnectionError
from clientes.aura.logger import logger

# Modificar la importación para manejar errores
try:
    from clientes.aura.utils.openai_client import get_openai_client
except ImportError:
    logger.warning("No se pudo importar get_openai_client, el diagnóstico con IA no estará disponible")
    
    # Definir una función de fallback para evitar errores
    def get_openai_client():
        """Función de respaldo cuando OpenAI no está disponible"""
        return None


class HTTPVerificador:
    """
    Verificador de rutas HTTP con capacidades avanzadas de diagnóstico.
    
    Esta clase se encarga de verificar la disponibilidad y estado de rutas
    HTTP en una aplicación Flask, con soporte para redirecciones, autenticación,
    diferentes métodos HTTP y reintentos automáticos.
    """
    
    def __init__(
        self,
        base_url: str = None,
        max_intentos: int = 3,
        timeout: int = 3,
        intervalo_reintento: float = 0.5,
        headers: Dict[str, str] = None,
        sesion_auth: Dict[str, str] = None
    ):
        """
        Inicializa el verificador HTTP con opciones configurables.
        
        Args:
            base_url (str, optional): URL base para las solicitudes. Si es None, 
                                      se usa 'http://localhost:5000'.
            max_intentos (int): Número máximo de intentos para solicitudes fallidas.
            timeout (int): Tiempo máximo de espera para cada solicitud en segundos.
            intervalo_reintento (float): Tiempo entre reintentos en segundos.
            headers (Dict[str, str], optional): Cabeceras HTTP personalizadas.
            sesion_auth (Dict[str, str], optional): Credenciales para autenticación.
        """
        self.base_url = base_url or os.getenv("VERIFICADOR_BASE_URL", "http://localhost:5000")
        self.max_intentos = max_intentos
        self.timeout = timeout
        self.intervalo_reintento = intervalo_reintento
        
        # Cabeceras predeterminadas
        self.headers = {
            'User-Agent': 'Verificador-Modulos/1.0',
        }
        
        # Agregar cabeceras personalizadas si se proporcionan
        if headers:
            self.headers.update(headers)
            
        self.sesion_auth = sesion_auth
        
        # Códigos de estado HTTP y sus diagnósticos
        self.diagnosticos_http = {
            200: {
                "existe": True,
                "causa": "✅ URL responde correctamente",
                "categoria": "success"
            },
            302: {
                "existe": True,
                "causa": "⚠️ URL redirecciona (verificar destino)",
                "categoria": "warning"
            },
            308: {
                "existe": True,
                "causa": "↪️ Redirecciona con 308: probablemente falta una '/' al final",
                "categoria": "warning"
            },
            400: {
                "existe": True,
                "causa": "❌ Solicitud incorrecta (Bad Request)",
                "categoria": "error"
            },
            401: {
                "existe": True,
                "causa": "❌ Se requiere autenticación",
                "categoria": "auth",
                "protegida": True
            },
            403: {
                "existe": True,
                "causa": "❌ Acceso prohibido (Forbidden)",
                "categoria": "auth",
                "protegida": True
            },
            404: {
                "existe": False,
                "causa": "❌ Ruta no encontrada en el servidor",
                "categoria": "error"
            },
            500: {
                "existe": False,
                "causa": "❌ Error interno del servidor",
                "categoria": "error"
            }
        }

    def verificar_ruta(
        self, 
        url: str, 
        metodo: str = "GET", 
        datos: Dict[str, Any] = None, 
        permitir_redirecciones: bool = False,
        reintentar_en_error: bool = True
    ) -> Dict[str, Any]:
        """
        Verifica una ruta HTTP y analiza su respuesta.
        
        Args:
            url (str): URL a verificar (relativa o absoluta)
            metodo (str): Método HTTP a utilizar (GET, POST, etc.)
            datos (Dict[str, Any], optional): Datos para enviar en la solicitud
            permitir_redirecciones (bool): Si se deben seguir las redirecciones
            reintentar_en_error (bool): Si se debe reintentar en caso de error
            
        Returns:
            Dict[str, Any]: Diagnóstico detallado de la ruta
        """
        # Normalizar URL
        url_completa = self._construir_url_completa(url)
        
        # Configuración de la solicitud
        kwargs = {
            "headers": self.headers,
            "allow_redirects": permitir_redirecciones,
            "timeout": self.timeout
        }
        
        # Agregar autenticación si está configurada
        if self.sesion_auth:
            kwargs["auth"] = (
                self.sesion_auth.get("username", ""),
                self.sesion_auth.get("password", "")
            )
            
        # Agregar datos según el método
        if metodo in ["POST", "PUT", "PATCH"] and datos:
            kwargs["json"] = datos
            
        # Realizar la solicitud con reintentos si está habilitado
        intentos = 1
        ultima_excepcion = None
        
        while intentos <= self.max_intentos:
            try:
                logger.debug(f"Verificando ruta: {metodo} {url_completa} (intento {intentos}/{self.max_intentos})")
                response = requests.request(metodo, url_completa, **kwargs)
                
                # Analizar la respuesta
                return self._analizar_respuesta(response, url)
                
            except Timeout as e:
                ultima_excepcion = e
                logger.warning(f"Timeout al verificar {url_completa} (intento {intentos}/{self.max_intentos})")
                
            except ConnectionError as e:
                ultima_excepcion = e
                logger.warning(f"Error de conexión al verificar {url_completa} (intento {intentos}/{self.max_intentos})")
                
            except Exception as e:
                ultima_excepcion = e
                logger.error(f"Error inesperado al verificar {url_completa}: {str(e)}")
                
                # No reintentar en caso de errores inesperados si no está habilitado
                if not reintentar_en_error:
                    break
            
            # Incrementar contador y esperar antes de reintentar
            intentos += 1
            if intentos <= self.max_intentos:
                time.sleep(self.intervalo_reintento)
                
        # Si llegamos aquí, todos los intentos fallaron
        return self._generar_respuesta_error(ultima_excepcion)

    def _construir_url_completa(self, url: str) -> str:
        """
        Construye la URL completa a partir de una URL relativa o absoluta.
        
        Args:
            url (str): URL a normalizar
            
        Returns:
            str: URL completa
        """
        # Si ya es una URL absoluta, devolverla tal cual
        if url.startswith(("http://", "https://")):
            return url
            
        # Normalizar URL relativa
        if not url.startswith('/'):
            url = '/' + url
            
        return f"{self.base_url}{url}"
        
    def _analizar_respuesta(self, response: requests.Response, url_original: str) -> Dict[str, Any]:
        """
        Analiza una respuesta HTTP y genera un diagnóstico.
        
        Args:
            response (requests.Response): Respuesta HTTP a analizar
            url_original (str): URL original que se solicitó
            
        Returns:
            Dict[str, Any]: Diagnóstico de la respuesta
        """
        status = response.status_code
        location = response.headers.get('Location')
        
        # Obtener diagnóstico base para este código de estado
        diagnostico = self.diagnosticos_http.get(status, {
            "existe": False,
            "causa": f"❓ Código de estado no catalogado: {status}",
            "categoria": "unknown"
        }).copy()
        
        # Añadir información básica
        diagnostico.update({
            "status": status,
            "location": location,
            "headers": dict(response.headers),
            "tiempo_respuesta": response.elapsed.total_seconds()
        })
        
        # Personalizar diagnóstico según casos especiales
        if status == 302 and location:
            if "/login" in location:
                diagnostico.update({
                    "existe": False,
                    "causa": "❌ Sesión no válida, redirigiendo a login",
                    "protegida_por_login": True
                })
                
        # Verificar si es una redirección 308 y probar con barra al final
        if status == 308 and not url_original.endswith('/'):
            retry_resultado = self._verificar_con_barra_final(url_original)
            if retry_resultado:
                diagnostico.update(retry_resultado)
                
        return diagnostico
        
    def _verificar_con_barra_final(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Verifica una URL añadiendo una barra final.
        
        Args:
            url (str): URL original sin barra final
            
        Returns:
            Optional[Dict[str, Any]]: Resultado de la verificación, o None si falló
        """
        try:
            url_con_barra = url if url.endswith('/') else f"{url}/"
            url_completa = self._construir_url_completa(url_con_barra)
            
            logger.info(f"Reintentando con barra final: {url_completa}")
            
            response = requests.get(
                url_completa,
                headers=self.headers,
                allow_redirects=False,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "existe": True,
                    "status": 200,
                    "causa": "✅ URL corregida al agregar '/' al final",
                    "location": url_con_barra,
                    "solucion_sugerida": "Agregar '/' al final de la ruta en las configuraciones del blueprint"
                }
                
        except Exception as e:
            logger.warning(f"Error al reintentar con barra final: {str(e)}")
            
        return None
        
    def _generar_respuesta_error(self, excepcion: Exception) -> Dict[str, Any]:
        """
        Genera una respuesta de error basada en la excepción.
        
        Args:
            excepcion (Exception): Excepción capturada
            
        Returns:
            Dict[str, Any]: Diagnóstico de error
        """
        if isinstance(excepcion, Timeout):
            return {
                "existe": False,
                "status": None,
                "causa": "⚠️ Tiempo de espera agotado",
                "categoria": "timeout",
                "location": None,
                "error": str(excepcion)
            }
        elif isinstance(excepcion, ConnectionError):
            return {
                "existe": False,
                "status": None,
                "causa": "❌ Error de conexión (¿servidor no iniciado?)",
                "categoria": "connection",
                "location": None,
                "error": str(excepcion)
            }
        else:
            return {
                "existe": False,
                "status": None,
                "causa": f"❌ Error inesperado: {str(excepcion)}",
                "categoria": "unknown",
                "location": None,
                "error": str(excepcion),
                "error_tipo": type(excepcion).__name__
            }

    # Añadir este nuevo método:
    def diagnosticar_con_ia(
        self, 
        resultado: Dict[str, Any], 
        codigo_fuente: str = None,
        contexto_adicional: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Utiliza IA para analizar y proporcionar un diagnóstico más detallado
        sobre un problema de ruta HTTP.
        
        Args:
            resultado: El resultado base del verificador HTTP
            codigo_fuente: Código fuente del blueprint o ruta relevante
            contexto_adicional: Información adicional útil para el análisis
            
        Returns:
            Dict[str, Any]: Diagnóstico enriquecido con análisis de IA
        """
        try:
            # Si la ruta ya funciona correctamente, no necesitamos diagnóstico de IA
            if resultado.get("status") == 200 or resultado.get("categoria") == "success":
                return resultado
                
            # Obtener cliente de OpenAI
            openai = get_openai_client()
            if not openai:
                logger.warning("No se pudo obtener cliente OpenAI para diagnóstico de ruta")
                return resultado
                
            # Preparar contexto para la IA
            prompt_context = {
                "resultado_http": {
                    "status": resultado.get("status"),
                    "causa": resultado.get("causa"),
                    "categoria": resultado.get("categoria"),
                    "location": resultado.get("location"),
                    "error": resultado.get("error") if "error" in resultado else None
                },
                "codigo_fuente": codigo_fuente if codigo_fuente else "No disponible",
                "contexto": contexto_adicional or {}
            }
            
            # Generar prompt para el modelo
            prompt = f"""
            Analiza este problema de ruta HTTP en una aplicación Flask y proporciona:
            1. Diagnóstico del problema
            2. Causa probable
            3. Solución recomendada con código de ejemplo si es apropiado
            
            Datos de la solicitud HTTP:
            {json.dumps(prompt_context, indent=2, ensure_ascii=False)}
            """
            
            # Realizar consulta a la API de OpenAI
            response = openai.chat.completions.create(
                model="gpt-4o",  # Usar el modelo disponible en el sistema
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en diagnóstico de rutas y problemas HTTP en aplicaciones Flask."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3  # Baja temperatura para respuestas más deterministas
            )
            
            # Extraer el análisis de IA
            analisis_ia = response.choices[0].message.content
            
            # Actualizar el resultado con el análisis de IA
            resultado.update({
                "analisis_ia": analisis_ia,
                "tiene_analisis_ia": True
            })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error al realizar diagnóstico con IA: {str(e)}")
            # Si falla el diagnóstico con IA, devolver el resultado original sin modificar
            return resultado

# Extender la función de verificación para incluir diagnóstico por IA cuando sea necesario
def verificar_respuesta_http(
    url: str, 
    usar_ia: bool = False,
    codigo_fuente: str = None,
    contexto_adicional: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Verifica la respuesta HTTP de una URL, manejando redirecciones y errores.
    Opcionalmente proporciona análisis con IA si se encuentran problemas.
    
    Args:
        url (str): URL a verificar, puede ser relativa (se le agrega el dominio)
        usar_ia (bool): Si debe utilizarse IA para diagnóstico avanzado
        codigo_fuente (str): Código fuente de la ruta (opcional)
        contexto_adicional (dict): Información adicional para análisis IA
    
    Returns:
        Dict[str, Any]: Información sobre la respuesta HTTP
    """
    verificador = HTTPVerificador()
    resultado = verificador.verificar_ruta(url)
    
    # Solo intentar análisis con IA si está activado y hay un problema
    if usar_ia and (resultado.get("status") != 200 or resultado.get("categoria") != "success"):
        try:
            # Verificar que la función get_openai_client existe y funciona
            if "get_openai_client" in globals() and get_openai_client():
                return verificador.diagnosticar_con_ia(resultado, codigo_fuente, contexto_adicional)
        except Exception as e:
            logger.error(f"Error al intentar diagnóstico con IA: {str(e)}")
    
    return resultado