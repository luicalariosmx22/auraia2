"""
Sistema de memoria temporal para respuestas inteligentes
Maneja el estado de conversación y opciones previas
"""

import json
import time
from typing import Dict, List, Optional
from clientes.aura.utils.supabase_client import supabase

class MemoriaConversacion:
    """Maneja la memoria temporal de conversaciones para respuestas inteligentes"""
    
    def __init__(self):
        self.cache_local = {}  # Cache en memoria para acceso rápido
        self.ttl_memoria = 1800  # 30 minutos de vida para la memoria
    
    def guardar_opciones(self, telefono: str, nombre_nora: str, opciones: List[Dict]) -> bool:
        """Guarda las opciones mostradas al usuario para la próxima interacción"""
        try:
            # Limpiar datos sensibles de las opciones para almacenar
            opciones_limpias = []
            for opcion in opciones:
                opciones_limpias.append({
                    'bloque': {
                        'id': opcion['bloque'].get('id'),
                        'contenido': opcion['bloque'].get('contenido'),
                        'etiquetas': opcion['bloque'].get('etiquetas', [])
                    },
                    'puntuacion': opcion.get('puntuacion', 0),
                    'razones': opcion.get('razones', []),
                    'tiene_duplicados': opcion.get('tiene_duplicados', False),
                    'num_similares': opcion.get('num_similares', 0)
                })
            
            datos_memoria = {
                'telefono': telefono,
                'nombre_nora': nombre_nora,
                'opciones': opciones_limpias,
                'timestamp': int(time.time()),
                'expira_en': int(time.time() + self.ttl_memoria)
            }
            
            # Guardar en cache local
            self.cache_local[f"{telefono}_{nombre_nora}"] = datos_memoria
            
            # Intentar guardar en base de datos (opcional, para persistencia)
            try:
                # Primero eliminar registros antiguos del mismo usuario
                supabase.table("memoria_conversacion") \
                    .delete() \
                    .eq("telefono", telefono) \
                    .eq("nombre_nora", nombre_nora) \
                    .execute()
                
                # Insertar nueva memoria
                supabase.table("memoria_conversacion") \
                    .insert({
                        'telefono': telefono,
                        'nombre_nora': nombre_nora,
                        'datos_memoria': json.dumps(opciones_limpias),
                        'timestamp': datos_memoria['timestamp'],
                        'expira_en': datos_memoria['expira_en']
                    }) \
                    .execute()
                    
            except Exception as e:
                print(f"⚠️ No se pudo guardar en BD, usando solo cache local: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando opciones en memoria: {e}")
            return False
    
    def obtener_opciones(self, telefono: str, nombre_nora: str) -> Optional[List[Dict]]:
        """Obtiene las opciones previamente mostradas al usuario"""
        try:
            clave = f"{telefono}_{nombre_nora}"
            
            # Primero buscar en cache local
            if clave in self.cache_local:
                datos = self.cache_local[clave]
                if datos['expira_en'] > int(time.time()):
                    return datos['opciones']
                else:
                    # Memoria expirada, limpiar
                    del self.cache_local[clave]
            
            # Buscar en base de datos
            try:
                response = supabase.table("memoria_conversacion") \
                    .select("datos_memoria, expira_en") \
                    .eq("telefono", telefono) \
                    .eq("nombre_nora", nombre_nora) \
                    .limit(1) \
                    .execute()
                
                if response.data:
                    datos = response.data[0]
                    if datos['expira_en'] > int(time.time()):
                        opciones = json.loads(datos['datos_memoria'])
                        # Actualizar cache local
                        self.cache_local[clave] = {
                            'opciones': opciones,
                            'timestamp': int(time.time()),
                            'expira_en': datos['expira_en']
                        }
                        return opciones
                    else:
                        # Memoria expirada, limpiar de BD
                        self.limpiar_memoria_expirada(telefono, nombre_nora)
                        
            except Exception as e:
                print(f"⚠️ Error accediendo a BD para memoria: {e}")
            
            return None
            
        except Exception as e:
            print(f"❌ Error obteniendo opciones de memoria: {e}")
            return None
    
    def limpiar_memoria(self, telefono: str, nombre_nora: str) -> bool:
        """Limpia la memoria de conversación de un usuario específico"""
        try:
            clave = f"{telefono}_{nombre_nora}"
            
            # Limpiar cache local
            if clave in self.cache_local:
                del self.cache_local[clave]
            
            # Limpiar de base de datos
            try:
                supabase.table("memoria_conversacion") \
                    .delete() \
                    .eq("telefono", telefono) \
                    .eq("nombre_nora", nombre_nora) \
                    .execute()
            except Exception as e:
                print(f"⚠️ Error limpiando memoria de BD: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error limpiando memoria: {e}")
            return False
    
    def limpiar_memoria_expirada(self, telefono: str = None, nombre_nora: str = None) -> bool:
        """Limpia memorias expiradas. Si no se especifica usuario, limpia todas las expiradas"""
        try:
            timestamp_actual = int(time.time())
            
            # Limpiar cache local
            claves_expiradas = []
            for clave, datos in self.cache_local.items():
                if datos['expira_en'] <= timestamp_actual:
                    if telefono and nombre_nora:
                        if clave == f"{telefono}_{nombre_nora}":
                            claves_expiradas.append(clave)
                    else:
                        claves_expiradas.append(clave)
            
            for clave in claves_expiradas:
                del self.cache_local[clave]
            
            # Limpiar de base de datos
            try:
                query = supabase.table("memoria_conversacion") \
                    .delete() \
                    .lt("expira_en", timestamp_actual)
                
                if telefono and nombre_nora:
                    query = query.eq("telefono", telefono).eq("nombre_nora", nombre_nora)
                
                query.execute()
                
            except Exception as e:
                print(f"⚠️ Error limpiando memoria expirada de BD: {e}")
            
            print(f"✅ Limpieza de memoria completada. Eliminadas {len(claves_expiradas)} entradas del cache")
            return True
            
        except Exception as e:
            print(f"❌ Error en limpieza de memoria expirada: {e}")
            return False

# Instancia global para uso en toda la aplicación
memoria_conversacion = MemoriaConversacion()
