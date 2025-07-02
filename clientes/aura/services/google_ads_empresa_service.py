# -*- coding: utf-8 -*-
"""
Servicio para gestionar la asociación de cuentas de Google Ads con empresas
"""

import logging
from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleAdsEmpresaService:
    """
    Servicio para asociar cuentas de Google Ads con empresas
    """
    
    def __init__(self):
        self.supabase = self._setup_supabase()
    
    def _setup_supabase(self) -> Client:
        """Configura el cliente de Supabase"""
        # Cargar variables de entorno
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env.local')
        load_dotenv(env_path)
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")  # Usar SUPABASE_KEY en lugar de SUPABASE_ANON_KEY
        
        if not url or not key:
            raise ValueError("Variables de entorno SUPABASE_URL y SUPABASE_KEY son requeridas")
        
        return create_client(url, key)
    
    def obtener_empresas_disponibles(self, nombre_nora: str) -> List[Dict]:
        """
        Obtiene las empresas disponibles para un cliente
        """
        try:
            response = self.supabase.table('cliente_empresas') \
                .select('id, nombre_empresa, descripcion') \
                .eq('nombre_nora', nombre_nora) \
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error obteniendo empresas para {nombre_nora}: {e}")
            return []
    
    def obtener_cuentas_asociadas(self, empresa_id: str) -> List[Dict]:
        """
        Obtiene las cuentas de Google Ads asociadas a una empresa
        """
        try:
            response = self.supabase.table('google_ads_cuentas_empresas') \
                .select('*') \
                .eq('empresa_id', empresa_id) \
                .eq('activa', True) \
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error obteniendo cuentas asociadas a empresa {empresa_id}: {e}")
            return []
    
    def asociar_cuenta_con_empresa(self, customer_id: str, empresa_id: str, 
                                 nombre_cuenta: str, cuenta_info: Dict) -> bool:
        """
        Asocia una cuenta de Google Ads con una empresa
        """
        try:
            # Preparar datos para insertar
            datos_cuenta = {
                'customer_id': customer_id,
                'empresa_id': empresa_id,
                'nombre_cuenta': nombre_cuenta,
                'moneda': cuenta_info.get('moneda', 'MXN'),
                'zona_horaria': cuenta_info.get('zona_horaria', 'America/Mexico_City'),
                'es_test': cuenta_info.get('es_test', False),
                'accesible': cuenta_info.get('accesible', True),
                'problema': cuenta_info.get('problema'),
                'activa': True
            }
            
            # Verificar si ya existe la asociación
            existing = self.supabase.table('google_ads_cuentas_empresas') \
                .select('id') \
                .eq('customer_id', customer_id) \
                .eq('empresa_id', empresa_id) \
                .execute()
            
            if existing.data:
                # Actualizar registro existente
                response = self.supabase.table('google_ads_cuentas_empresas') \
                    .update(datos_cuenta) \
                    .eq('customer_id', customer_id) \
                    .eq('empresa_id', empresa_id) \
                    .execute()
                logger.info(f"✅ Actualizada asociación: {customer_id} -> {empresa_id}")
            else:
                # Crear nueva asociación
                response = self.supabase.table('google_ads_cuentas_empresas') \
                    .insert(datos_cuenta) \
                    .execute()
                logger.info(f"✅ Creada nueva asociación: {customer_id} -> {empresa_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error asociando cuenta {customer_id} con empresa {empresa_id}: {e}")
            return False
    
    def desasociar_cuenta(self, customer_id: str, empresa_id: str) -> bool:
        """
        Desasocia una cuenta de Google Ads de una empresa (la marca como inactiva)
        """
        try:
            response = self.supabase.table('google_ads_cuentas_empresas') \
                .update({'activa': False}) \
                .eq('customer_id', customer_id) \
                .eq('empresa_id', empresa_id) \
                .execute()
            
            logger.info(f"✅ Desasociada cuenta {customer_id} de empresa {empresa_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error desasociando cuenta {customer_id} de empresa {empresa_id}: {e}")
            return False
    
    def asociar_cuentas_automaticamente(self, nombre_nora: str, cuentas_google_ads: List[Dict]) -> Dict:
        """
        Asocia automáticamente cuentas de Google Ads con empresas basándose en nombres
        """
        try:
            # Obtener empresas disponibles
            empresas = self.obtener_empresas_disponibles(nombre_nora)
            
            if not empresas:
                logger.warning(f"No se encontraron empresas para {nombre_nora}")
                return {"asociadas": 0, "errores": [], "total": len(cuentas_google_ads)}
            
            asociadas = 0
            errores = []
            
            # Mapeo inteligente basado en nombres
            for cuenta in cuentas_google_ads:
                customer_id = cuenta['id']
                nombre_cuenta = cuenta['nombre']
                
                # Buscar empresa que coincida por nombre
                empresa_encontrada = None
                for empresa in empresas:
                    nombre_empresa = empresa['nombre_empresa'].lower()
                    nombre_cuenta_lower = nombre_cuenta.lower()
                    
                    # Verificar coincidencias
                    if (nombre_empresa in nombre_cuenta_lower or 
                        nombre_cuenta_lower in nombre_empresa or
                        self._calcular_similitud(nombre_empresa, nombre_cuenta_lower) > 0.7):
                        empresa_encontrada = empresa
                        break
                
                if empresa_encontrada:
                    # Asociar cuenta con empresa
                    if self.asociar_cuenta_con_empresa(
                        customer_id, 
                        empresa_encontrada['id'], 
                        nombre_cuenta, 
                        cuenta
                    ):
                        asociadas += 1
                        logger.info(f"✅ Asociada: {nombre_cuenta} -> {empresa_encontrada['nombre_empresa']}")
                    else:
                        errores.append(f"Error asociando {nombre_cuenta}")
                else:
                    # Si no encuentra coincidencia, asociar con la primera empresa disponible
                    if empresas:
                        if self.asociar_cuenta_con_empresa(
                            customer_id, 
                            empresas[0]['id'], 
                            nombre_cuenta, 
                            cuenta
                        ):
                            asociadas += 1
                            logger.info(f"✅ Asociada por defecto: {nombre_cuenta} -> {empresas[0]['nombre_empresa']}")
                        else:
                            errores.append(f"Error asociando {nombre_cuenta} por defecto")
            
            return {
                "asociadas": asociadas,
                "errores": errores,
                "total": len(cuentas_google_ads)
            }
            
        except Exception as e:
            logger.error(f"Error en asociación automática: {e}")
            return {"asociadas": 0, "errores": [str(e)], "total": len(cuentas_google_ads)}
    
    def _calcular_similitud(self, texto1: str, texto2: str) -> float:
        """
        Calcula similitud básica entre dos textos
        """
        if not texto1 or not texto2:
            return 0.0
        
        # Contar palabras comunes
        palabras1 = set(texto1.lower().split())
        palabras2 = set(texto2.lower().split())
        
        interseccion = len(palabras1.intersection(palabras2))
        union = len(palabras1.union(palabras2))
        
        return interseccion / union if union > 0 else 0.0
    
    def obtener_resumen_asociaciones(self, nombre_nora: str) -> Dict:
        """
        Obtiene un resumen de las asociaciones de cuentas para un cliente
        """
        try:
            # Obtener empresas del cliente
            empresas = self.obtener_empresas_disponibles(nombre_nora)
            
            resumen = {
                "total_empresas": len(empresas),
                "total_cuentas_asociadas": 0,
                "empresas_con_cuentas": 0,
                "detalle_empresas": []
            }
            
            for empresa in empresas:
                cuentas = self.obtener_cuentas_asociadas(empresa['id'])
                
                detalle_empresa = {
                    "empresa": empresa,
                    "cuentas": cuentas,
                    "total_cuentas": len(cuentas),
                    "cuentas_accesibles": len([c for c in cuentas if c.get('accesible', True)]),
                    "cuentas_con_problemas": len([c for c in cuentas if not c.get('accesible', True)])
                }
                
                resumen["detalle_empresas"].append(detalle_empresa)
                resumen["total_cuentas_asociadas"] += len(cuentas)
                
                if cuentas:
                    resumen["empresas_con_cuentas"] += 1
            
            return resumen
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de asociaciones: {e}")
            return {"error": str(e)}

# Crear instancia global del servicio
google_ads_empresa_service = GoogleAdsEmpresaService()
