"""
Sistema de ejecución de automatizaciones
Ejecuta las tareas programadas según su frecuencia y parámetros
"""

import os
import json
import importlib
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase

class EjecutorAutomatizaciones:
    """
    Clase para manejar la ejecución de automatizaciones
    """
    
    def __init__(self):
        self.modulos_disponibles = {
            'automatizaciones_ejecutor': 'clientes.aura.utils.automatizaciones_ejecutor',
            'reportes': 'clientes.aura.utils.reportes',
            'notificaciones': 'clientes.aura.utils.notificaciones',
            'google_ads': 'clientes.aura.utils.google_ads_utils',
            'meta_ads': 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads',
            'meta_ads_sincronizador': 'clientes.aura.routes.panel_cliente_meta_ads.sincronizador_semanal',
            'sincronizador_semanal': 'clientes.aura.routes.panel_cliente_meta_ads.sincronizador_semanal',
            'tareas': 'clientes.aura.utils.tareas_utils',
            'backup': 'clientes.aura.utils.backup_utils',
            'contactos': 'clientes.aura.routes.panel_cliente_contactos.panel_cliente_contactos',
            'pagos': 'clientes.aura.routes.panel_cliente_pagos.panel_cliente_pagos'
        }
    
    def ejecutar_automatizaciones_pendientes(self):
        """
        Ejecuta todas las automatizaciones que tienen fecha/hora de ejecución vencida
        """
        try:
            # Obtener automatizaciones activas y pendientes
            ahora = datetime.now()
            
            response = supabase.table("automatizaciones") \
                .select("*") \
                .eq("activo", True) \
                .lte("proxima_ejecucion", ahora.isoformat()) \
                .execute()
            
            automatizaciones_pendientes = response.data if response.data else []
            
            print(f"🤖 Encontradas {len(automatizaciones_pendientes)} automatizaciones pendientes")
            
            resultados = []
            
            for automatizacion in automatizaciones_pendientes:
                resultado = self.ejecutar_automatizacion(automatizacion)
                resultados.append(resultado)
                
                # Actualizar próxima ejecución si fue exitosa
                if resultado['success']:
                    self.actualizar_proxima_ejecucion(automatizacion)
            
            return {
                'success': True,
                'ejecutadas': len([r for r in resultados if r['success']]),
                'fallidas': len([r for r in resultados if not r['success']]),
                'resultados': resultados
            }
            
        except Exception as e:
            print(f"❌ Error al ejecutar automatizaciones: {e}")
            return {
                'success': False,
                'error': str(e),
                'ejecutadas': 0,
                'fallidas': 0,
                'resultados': []
            }
    
    def ejecutar_automatizacion(self, automatizacion):
        """
        Ejecuta una automatización específica
        """
        try:
            print(f"🔄 Ejecutando: {automatizacion['nombre']}")
            
            # Obtener módulo y función
            modulo_nombre = automatizacion.get('modulo_relacionado')
            funcion_nombre = automatizacion.get('funcion_objetivo')
            parametros = automatizacion.get('parametros_json', {})
            
            if not modulo_nombre or not funcion_nombre:
                raise ValueError("Módulo o función no especificados")
            
            # Importar módulo dinámicamente
            if modulo_nombre in self.modulos_disponibles:
                modulo_path = self.modulos_disponibles[modulo_nombre]
                modulo = importlib.import_module(modulo_path)
            else:
                # Intentar importar directamente
                modulo = importlib.import_module(modulo_nombre)
            
            # Obtener función
            if not hasattr(modulo, funcion_nombre):
                raise AttributeError(f"Función '{funcion_nombre}' no encontrada en '{modulo_nombre}'")
            
            funcion = getattr(modulo, funcion_nombre)
            
            # Ejecutar función con parámetros
            if parametros:
                resultado_funcion = funcion(**parametros)
            else:
                resultado_funcion = funcion()
            
            # Actualizar registro de ejecución
            self.registrar_ejecucion(automatizacion['id'], True, str(resultado_funcion))
            
            return {
                'success': True,
                'automatizacion_id': automatizacion['id'],
                'nombre': automatizacion['nombre'],
                'resultado': resultado_funcion,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error ejecutando {automatizacion['nombre']}: {e}")
            
            # Registrar error
            self.registrar_ejecucion(automatizacion['id'], False, str(e))
            
            return {
                'success': False,
                'automatizacion_id': automatizacion['id'],
                'nombre': automatizacion['nombre'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def registrar_ejecucion(self, automatizacion_id, success, detalle):
        """
        Registra la ejecución de una automatización en la base de datos
        """
        try:
            ahora = datetime.now()
            
            # Actualizar última ejecución
            supabase.table("automatizaciones") \
                .update({
                    "ultima_ejecucion": ahora.isoformat(),
                    "actualizado_en": ahora.isoformat()
                }) \
                .eq("id", automatizacion_id) \
                .execute()
            
            # Aquí podrías crear una tabla de logs de ejecución si la necesitas
            # supabase.table("logs_automatizaciones").insert({...}).execute()
            
            print(f"✅ Registro de ejecución actualizado para {automatizacion_id}")
            
        except Exception as e:
            print(f"❌ Error al registrar ejecución: {e}")
    
    def actualizar_proxima_ejecucion(self, automatizacion):
        """
        Calcula y actualiza la próxima fecha de ejecución
        """
        try:
            from clientes.aura.routes.panel_cliente_automatizaciones.panel_cliente_automatizaciones import calcular_proxima_ejecucion
            
            proxima = calcular_proxima_ejecucion(
                automatizacion['frecuencia'],
                automatizacion['hora_ejecucion']
            )
            
            supabase.table("automatizaciones") \
                .update({
                    "proxima_ejecucion": proxima.isoformat(),
                    "actualizado_en": datetime.now().isoformat()
                }) \
                .eq("id", automatizacion['id']) \
                .execute()
            
            print(f"🕒 Próxima ejecución programada: {proxima.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error al actualizar próxima ejecución: {e}")
    
    def ejecutar_por_id(self, automatizacion_id):
        """
        Ejecuta una automatización específica por su ID
        """
        try:
            response = supabase.table("automatizaciones") \
                .select("*") \
                .eq("id", automatizacion_id) \
                .execute()
            
            if not response.data:
                return {
                    'success': False,
                    'error': 'Automatización no encontrada'
                }
            
            automatizacion = response.data[0]
            return self.ejecutar_automatizacion(automatizacion)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Funciones de ejemplo para automatizaciones
def ejemplo_reporte_diario():
    """
    Función de ejemplo para generar reporte diario
    """
    print("📊 Generando reporte diario...")
    # Aquí iría la lógica real del reporte
    return "Reporte diario generado exitosamente"

def ejemplo_backup_semanal():
    """
    Función de ejemplo para backup semanal
    """
    print("💾 Ejecutando backup semanal...")
    # Aquí iría la lógica real del backup
    return "Backup semanal completado"

def ejemplo_limpieza_logs(dias_antiguedad=30):
    """
    Función de ejemplo para limpiar logs antiguos
    """
    print(f"🧹 Limpiando logs de más de {dias_antiguedad} días...")
    # Aquí iría la lógica real de limpieza
    return f"Logs antiguos limpiados (más de {dias_antiguedad} días)"

def ejemplo_sincronizacion_datos():
    """
    Función de ejemplo para sincronizar datos
    """
    print("🔄 Sincronizando datos...")
    # Aquí iría la lógica real de sincronización
    return "Sincronización de datos completada"

# Instancia global del ejecutor
ejecutor = EjecutorAutomatizaciones()
