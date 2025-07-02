# -*- coding: utf-8 -*-
"""
Servicio mejorado para gestionar empresas y cuentas de Google Ads
Conecta con la base de datos real (Supabase) para manejar múltiples empresas
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class GoogleAdsEmpresaServiceMejorado:
    """
    Servicio para gestionar la asociación de cuentas de Google Ads con empresas
    Se conecta a la base de datos real para obtener empresas del cliente
    """
    
    def __init__(self):
        self.supabase = self._setup_supabase()
    
    def _setup_supabase(self):
        """Configura la conexión a Supabase"""
        try:
            # Cargar variables de entorno
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env.local')
            load_dotenv(env_path)
            
            # Obtener credenciales de Supabase
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")  # Usar SUPABASE_KEY en lugar de SUPABASE_ANON_KEY
            
            if not supabase_url or not supabase_key:
                logger.warning("⚠️ Credenciales de Supabase no encontradas, usando modo mock")
                return None
            
            from supabase import create_client
            client = create_client(supabase_url, supabase_key)
            
            logger.info("✅ Cliente Supabase configurado correctamente")
            return client
            
        except ImportError:
            logger.warning("⚠️ Módulo supabase no instalado, usando modo mock")
            return None
        except Exception as e:
            logger.error(f"❌ Error configurando Supabase: {e}")
            return None
    
    def obtener_empresas_disponibles(self, nombre_nora: str, filtro: str = None, limit: int = 50) -> List[Dict]:
        """
        Obtiene empresas disponibles para un cliente específico
        
        Args:
            nombre_nora: Nombre del cliente (ej: 'aura')
            filtro: Filtro de búsqueda por nombre de empresa (opcional)
            limit: Límite de resultados (default: 50)
        """
        if not self.supabase:
            # Modo mock para desarrollo
            return self._obtener_empresas_mock(nombre_nora, filtro, limit)
        
        try:
            # Construir query base
            query = self.supabase.table('cliente_empresas').select('*').eq('nombre_nora', nombre_nora).eq('activo', True)
            
            # Aplicar filtro de búsqueda si se proporciona
            if filtro:
                query = query.ilike('nombre_empresa', f'%{filtro}%')
            
            # Aplicar límite y ordenar
            query = query.order('nombre_empresa').limit(limit)
            
            # Ejecutar query
            response = query.execute()
            
            if response.data:
                empresas = []
                for empresa in response.data:
                    empresas.append({
                        'id': empresa['id'],
                        'nombre': empresa['nombre_empresa'],
                        'giro': empresa.get('giro', ''),
                        'activa': empresa.get('activo', True),
                        'ciudad': empresa.get('ciudad', ''),
                        'estado': empresa.get('estado', '')
                    })
                
                logger.info(f"✅ Encontradas {len(empresas)} empresas para {nombre_nora}")
                return empresas
            else:
                logger.warning(f"⚠️ No se encontraron empresas para {nombre_nora}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo empresas para {nombre_nora}: {e}")
            # Fallback a modo mock en caso de error
            return self._obtener_empresas_mock(nombre_nora, filtro, limit)
    
    def _obtener_empresas_mock(self, nombre_nora: str, filtro: str = None, limit: int = 50) -> List[Dict]:
        """Empresas mock para desarrollo cuando no hay conexión a DB"""
        empresas_mock = [
            {"id": "empresa-1", "nombre": "LaReina Pasteleria", "giro": "Alimentaria", "activa": True, "ciudad": "México", "estado": "CDMX"},
            {"id": "empresa-2", "nombre": "Musicando", "giro": "Entretenimiento", "activa": True, "ciudad": "Guadalajara", "estado": "Jalisco"},
            {"id": "empresa-3", "nombre": "RIMS 2", "giro": "Automotriz", "activa": True, "ciudad": "Monterrey", "estado": "Nuevo León"},
            {"id": "empresa-4", "nombre": "SAL DE JADE", "giro": "Restaurante", "activa": True, "ciudad": "Puebla", "estado": "Puebla"},
            {"id": "empresa-5", "nombre": "Suspiros Cakes", "giro": "Alimentaria", "activa": True, "ciudad": "Querétaro", "estado": "Querétaro"},
            {"id": "empresa-6", "nombre": "Suspiros Pastelerías", "giro": "Alimentaria", "activa": True, "ciudad": "León", "estado": "Guanajuato"},
            {"id": "empresa-7", "nombre": "Vetervan", "giro": "Veterinaria", "activa": True, "ciudad": "Mérida", "estado": "Yucatán"},
            # Empresas adicionales para simular múltiples empresas
            {"id": "empresa-8", "nombre": "Cafe Central", "giro": "Alimentaria", "activa": True, "ciudad": "Oaxaca", "estado": "Oaxaca"},
            {"id": "empresa-9", "nombre": "Delicias Gourmet", "giro": "Alimentaria", "activa": True, "ciudad": "Morelia", "estado": "Michoacán"},
            {"id": "empresa-10", "nombre": "Tech Solutions", "giro": "Tecnología", "activa": True, "ciudad": "Tijuana", "estado": "Baja California"},
        ]
        
        # Aplicar filtro si se proporciona
        if filtro:
            empresas_filtradas = [e for e in empresas_mock if filtro.lower() in e['nombre'].lower()]
        else:
            empresas_filtradas = empresas_mock
        
        # Aplicar límite
        return empresas_filtradas[:limit]
    
    def buscar_empresas(self, nombre_nora: str, termino_busqueda: str) -> List[Dict]:
        """
        Busca empresas por término de búsqueda
        """
        return self.obtener_empresas_disponibles(nombre_nora, filtro=termino_busqueda, limit=20)
    
    def obtener_empresa_por_cuenta(self, customer_id: str) -> Optional[Dict]:
        """
        Obtiene la empresa asociada a una cuenta de Google Ads
        """
        if not self.supabase:
            # Modo mock
            asociaciones_mock = {
                "3700518858": {"empresa_id": "empresa-1", "nombre": "LaReina Pasteleria"},
                "1785583613": {"empresa_id": "empresa-2", "nombre": "Musicando"},
                "4890270350": {"empresa_id": "empresa-3", "nombre": "RIMS 2"},
                "9737121597": {"empresa_id": "empresa-4", "nombre": "SAL DE JADE"},
                "7605115009": {"empresa_id": "empresa-5", "nombre": "Suspiros Cakes"},
                "1554994188": {"empresa_id": "empresa-6", "nombre": "Suspiros Pastelerías"},
                "5291123262": {"empresa_id": "empresa-7", "nombre": "Vetervan"}
            }
            
            if customer_id in asociaciones_mock:
                asociacion = asociaciones_mock[customer_id]
                return {
                    "id": asociacion["empresa_id"],
                    "nombre": asociacion["nombre"]
                }
            return None
        
        try:
            # Consultar asociación en la base de datos
            response = self.supabase.table('google_ads_cuentas_empresas').select('''
                empresa_id,
                cliente_empresas!inner(id, nombre_empresa)
            ''').eq('customer_id', customer_id).execute()
            
            if response.data and len(response.data) > 0:
                asociacion = response.data[0]
                empresa = asociacion['cliente_empresas']
                return {
                    "id": empresa['id'],
                    "nombre": empresa['nombre_empresa']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo empresa para cuenta {customer_id}: {e}")
            return None
    
    def asociar_cuenta_empresa(self, customer_id: str, empresa_id: str, nombre_nora: str) -> bool:
        """
        Asocia una cuenta de Google Ads con una empresa
        """
        if not self.supabase:
            # Modo mock - solo log
            logger.info(f"📝 [MOCK] Asociando cuenta {customer_id} con empresa {empresa_id}")
            return True
        
        try:
            # Verificar que la empresa existe y pertenece al cliente
            empresa_response = self.supabase.table('cliente_empresas').select('*').eq('id', empresa_id).eq('nombre_nora', nombre_nora).execute()
            
            if not empresa_response.data:
                logger.error(f"❌ Empresa {empresa_id} no encontrada para cliente {nombre_nora}")
                return False
            
            empresa = empresa_response.data[0]
            
            # Insertar o actualizar asociación
            asociacion_data = {
                'customer_id': customer_id,
                'empresa_id': empresa_id,
                'nombre_cuenta': f"Cuenta {customer_id}",  # Esto podría mejorarse con el nombre real de la API
                'activa': True
            }
            
            # Usar upsert para insertar o actualizar
            response = self.supabase.table('google_ads_cuentas_empresas').upsert(
                asociacion_data,
                on_conflict='customer_id'
            ).execute()
            
            if response.data:
                logger.info(f"✅ Cuenta {customer_id} asociada exitosamente con empresa {empresa['nombre_empresa']}")
                return True
            else:
                logger.error(f"❌ Error en respuesta al asociar cuenta {customer_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error asociando cuenta {customer_id} con empresa {empresa_id}: {e}")
            return False
    
    def obtener_estadisticas_empresas(self, nombre_nora: str) -> Dict:
        """
        Obtiene estadísticas de empresas y cuentas para el dashboard
        """
        try:
            if not self.supabase:
                return {
                    'total_empresas': 10,
                    'empresas_con_google_ads': 7,
                    'cuentas_google_ads_total': 7,
                    'cuentas_activas': 7
                }
            
            # Contar empresas total
            empresas_response = self.supabase.table('cliente_empresas').select('id', count='exact').eq('nombre_nora', nombre_nora).eq('activo', True).execute()
            total_empresas = empresas_response.count or 0
            
            # Contar empresas con Google Ads
            empresas_con_ads_response = self.supabase.table('google_ads_cuentas_empresas').select('''
                empresa_id,
                cliente_empresas!inner(nombre_nora)
            ''', count='exact').eq('cliente_empresas.nombre_nora', nombre_nora).execute()
            
            empresas_con_google_ads = len(set([r['empresa_id'] for r in empresas_con_ads_response.data])) if empresas_con_ads_response.data else 0
            
            # Contar cuentas de Google Ads total
            cuentas_total_response = self.supabase.table('google_ads_cuentas_empresas').select('''
                customer_id,
                cliente_empresas!inner(nombre_nora)
            ''', count='exact').eq('cliente_empresas.nombre_nora', nombre_nora).execute()
            
            cuentas_google_ads_total = cuentas_total_response.count or 0
            
            # Contar cuentas activas
            cuentas_activas_response = self.supabase.table('google_ads_cuentas_empresas').select('''
                customer_id,
                cliente_empresas!inner(nombre_nora)
            ''', count='exact').eq('cliente_empresas.nombre_nora', nombre_nora).eq('activa', True).execute()
            
            cuentas_activas = cuentas_activas_response.count or 0
            
            return {
                'total_empresas': total_empresas,
                'empresas_con_google_ads': empresas_con_google_ads,
                'cuentas_google_ads_total': cuentas_google_ads_total,
                'cuentas_activas': cuentas_activas
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas para {nombre_nora}: {e}")
            return {
                'total_empresas': 0,
                'empresas_con_google_ads': 0,
                'cuentas_google_ads_total': 0,
                'cuentas_activas': 0
            }

# Crear instancia global
google_ads_empresa_service_mejorado = GoogleAdsEmpresaServiceMejorado()
