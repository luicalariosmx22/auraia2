from typing import List, Dict, Any

def generar_explicacion_errores(modulo: dict) -> list[str]:
    """
    Genera explicaciones amigables para los errores detectados en el módulo.
    
    Args:
        modulo (dict): Diccionario con la información del módulo analizado
        
    Returns:
        list[str]: Lista de explicaciones en formato amigable
    """
    explicaciones = []

    # 1. Verificar estructura de archivos
    if not modulo.get("carpeta_backend"):
        explicaciones.append(
            "❌ No se encontró la carpeta backend del módulo. "
            "Asegúrate de que exista en 'clientes/aura/routes'."
        )

    if not modulo.get("existe_archivo"):
        explicaciones.append(
            f"❌ No se encontró el archivo principal '{modulo.get('nombre_archivo_principal')}'. "
            "Verifica el nombre y ubicación del archivo."
        )
    elif modulo.get("validacion", {}).get("errores"):
        errores_ia = ", ".join(modulo["validacion"]["errores"])
        explicaciones.append(
            f"⚠️ El archivo principal tiene errores de estructura: {errores_ia}"
        )

    # 2. Verificar registro y configuración
    if not modulo.get("registrado_codigo"):
        explicaciones.append(
            "❌ El módulo no está registrado correctamente en 'registro_dinamico.py'. "
            "Revisa que esté importado y registrado con safe_register_blueprint()."
        )
        
        # Añadir detalles del registro si están disponibles
        if modulo.get("detalles_registro", {}).get("diagnostico"):
            for detalle in modulo["detalles_registro"]["diagnostico"]:
                explicaciones.append(f"  → {detalle}")
    
    # Verificar si el módulo está activado en alguna Nora
    if not modulo.get("activado_en") or len(modulo["activado_en"]) == 0:
        explicaciones.append("❌ No está activo en ninguna Nora")
        
    if not modulo.get("menciones_en_init"):
        explicaciones.append(
            "⚠️ El módulo no fue encontrado en '__init__.py'. "
            "Esto puede impedir su carga por Flask."
        )

    # 3. Verificar rutas y respuestas HTTP
    if modulo.get("protegida_por_login"):
        explicaciones.append("🔒 Esta ruta está protegida por login. Considera iniciar sesión antes de probarla.")
    elif not modulo.get("existe_ruta"):
        explicacion_base = (
            f"❌ La ruta '/panel_cliente/{{nombre}}/{modulo['nombre']}' "
            "no responde correctamente."
        )
        
        if modulo.get("explicacion_http"):
            explicacion_base += f" Causa: {modulo['explicacion_http']}"
            
        if modulo.get("respuesta_http"):
            explicacion_base += f" (HTTP {modulo['respuesta_http']})"
            
        explicaciones.append(explicacion_base)

    # 4. Verificar registro dinámico con IA
    if modulo.get("registro_dinamico_ia"):
        ia_info = modulo["registro_dinamico_ia"]
        if not ia_info.get("parece_registrado"):
            explicaciones.append(
                "🧠 Análisis IA: El módulo podría no estar correctamente registrado. "
                f"({ia_info.get('detalle', 'Sin detalles')})"
            )

    return explicaciones

def diagnosticar_modulo_avanzado(modulo: dict) -> dict:
    """
    Realiza un diagnóstico avanzado del módulo para encontrar problemas comunes.
    
    Args:
        modulo (dict): Información del módulo
        
    Returns:
        dict: Diagnóstico detallado
    """
    diagnostico = {
        "tiene_problemas": False,
        "gravedad": "bajo",
        "problemas": [],
        "recomendaciones": []
    }
    
    problemas = []
    
    # Verificar problemas críticos
    if not modulo.get("existe_archivo"):
        problemas.append({
            "tipo": "critico",
            "mensaje": f"No existe el archivo principal '{modulo.get('nombre_archivo_principal')}'",
            "solucion": f"Crear el archivo en clientes/aura/routes/panel_cliente_{modulo['nombre']}/{modulo.get('nombre_archivo_principal')}"
        })
        diagnostico["gravedad"] = "alto"
    
    if not modulo.get("registrado_codigo") and not modulo.get("registro_dinamico_ia", {}).get("parece_registrado"):
        problemas.append({
            "tipo": "critico",
            "mensaje": "El módulo no está registrado en registro_dinamico.py",
            "solucion": "Utiliza la sugerencia de código generada para registrarlo correctamente"
        })
        diagnostico["gravedad"] = "alto"
        
    # Verificar problemas medios
    if not modulo.get("menciones_en_init"):
        problemas.append({
            "tipo": "medio",
            "mensaje": "No hay menciones del módulo en __init__.py",
            "solucion": "Verifica si el módulo necesita ser importado explícitamente"
        })
        if diagnostico["gravedad"] == "bajo":
            diagnostico["gravedad"] = "medio"
            
    if modulo.get("respuesta_http") and modulo["respuesta_http"] not in [200, 302]:
        problemas.append({
            "tipo": "medio",
            "mensaje": f"La ruta HTTP devuelve código {modulo.get('respuesta_http')}",
            "solucion": "Verifica la implementación de las rutas Flask y su registro"
        })
        if diagnostico["gravedad"] == "bajo":
            diagnostico["gravedad"] = "medio"
    
    # Verificar advertencias
    if not modulo.get("templates_encontrados"):
        problemas.append({
            "tipo": "bajo",
            "mensaje": "No se encontraron templates para este módulo",
            "solucion": "Crea la carpeta de templates correspondiente si el módulo necesita vistas"
        })
    
    # Actualizar diagnóstico final
    diagnostico["tiene_problemas"] = len(problemas) > 0
    diagnostico["problemas"] = problemas
    
    # Generar recomendaciones generales
    if diagnostico["tiene_problemas"]:
        if diagnostico["gravedad"] == "alto":
            diagnostico["recomendaciones"].append("Corrige los problemas críticos primero")
        elif diagnostico["gravedad"] == "medio":
            diagnostico["recomendaciones"].append("Revisa la estructura del módulo y su registro")
        else:
            diagnostico["recomendaciones"].append("Considera mejorar la organización del módulo")
    
    return diagnostico