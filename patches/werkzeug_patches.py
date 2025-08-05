"""
Parches para solucionar problemas de compatibilidad con Werkzeug y Flask-Session.

Este módulo contiene funciones que reemplazan comportamientos problemáticos
en las bibliotecas de Werkzeug para garantizar la compatibilidad con la
aplicación AuraAi2, especialmente con el manejo de sesiones.
"""
import logging
import re

logger = logging.getLogger(__name__)

def apply_patches():
    """
    Aplica todos los parches necesarios a Werkzeug y Flask-Session.
    
    Esta función debe llamarse antes de importar Flask o cualquier otra
    biblioteca que use Werkzeug.
    """
    # Patch para el problema de cookies en bytes
    patch_werkzeug_dump_cookie()
    
    # Patch para Flask-Session
    patch_flask_session()
    
    logger.info("✅ Parches aplicados correctamente")

def patch_werkzeug_dump_cookie():
    """
    Reemplaza werkzeug.http.dump_cookie para manejar valores de tipo bytes.
    
    Esta función sustituye por completo la implementación de dump_cookie
    para asegurar que los valores bytes se conviertan a strings.
    """
    try:
        import werkzeug.http
        original_dump_cookie = werkzeug.http.dump_cookie
        
        def patched_dump_cookie(key, value=None, max_age=None, expires=None,
                             path='/', domain=None, secure=False, httponly=False,
                             charset='utf-8', sync_expires=True, max_size=4093,
                             samesite=None):
            """
            Versión modificada de dump_cookie que maneja valores de tipo bytes.
            
            Args:
                key: Nombre de la cookie
                value: Valor de la cookie (puede ser bytes o string)
                max_age: Tiempo máximo de vida en segundos
                expires: Fecha de expiración
                path: Ruta de la cookie
                domain: Dominio de la cookie
                secure: Si la cookie solo se envía por HTTPS
                httponly: Si la cookie solo es accesible por HTTP
                charset: Charset para codificar/decodificar
                sync_expires: Si sincroniza max_age y expires
                max_size: Tamaño máximo de la cookie
                samesite: Política SameSite (None, Lax o Strict)
                
            Returns:
                str: Cadena de texto que representa la cookie
            """
            # Convertir el valor a string si es bytes
            if isinstance(value, bytes):
                try:
                    value = value.decode(charset)
                    logger.debug(f"Valor de cookie convertido de bytes a string: {key}")
                except UnicodeDecodeError:
                    value = value.hex()
                    logger.debug(f"Valor de cookie {key} convertido a representación hexadecimal")
            
            # Llamar a la implementación original con el valor convertido
            return original_dump_cookie(key, value, max_age, expires, path, domain, 
                                      secure, httponly, charset, sync_expires, 
                                      max_size, samesite)
        
        # Aplicar el parche
        werkzeug.http.dump_cookie = patched_dump_cookie
        logger.info("✅ Patch werkzeug.http.dump_cookie aplicado")
    except Exception as e:
        logger.error(f"Error al aplicar patch werkzeug.http.dump_cookie: {str(e)}", exc_info=True)
        raise

def patch_flask_session():
    """
    Modifica Flask-Session para evitar problemas con IDs de sesión en bytes.
    """
    try:
        from flask_session import sessions
        
        # Guardar la implementación original
        original_save_session = sessions.SessionInterface.save_session
        
        def safe_save_session(self, app, session, response):
            """
            Versión segura de save_session que maneja IDs de sesión en bytes.
            """
            # Si hay un ID de sesión en bytes, convertirlo a string
            if hasattr(session, 'sid') and session.sid is not None and isinstance(session.sid, bytes):
                try:
                    session.sid = session.sid.decode('utf-8')
                except UnicodeDecodeError:
                    session.sid = session.sid.hex()
                logger.debug(f"ID de sesión convertido de bytes a string")
            
            # Llamar a la implementación original
            return original_save_session(self, app, session, response)
        
        # Aplicar el parche
        sessions.SessionInterface.save_session = safe_save_session
        logger.info("✅ Patch para Flask-Session aplicado")
    except ImportError:
        logger.warning("⚠️ No se pudo importar flask_session, omitiendo parche")
    except Exception as e:
        logger.error(f"Error al aplicar patch para Flask-Session: {str(e)}", exc_info=True)