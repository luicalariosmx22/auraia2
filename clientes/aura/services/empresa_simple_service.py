# -*- coding: utf-8 -*-
"""
Servicio para gestionar empresas y cuentas de Google Ads
Versión que respeta la estructura de cliente_empresas
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class EmpresaSimpleService:
    """
    Servicio para gestionar empresas del cliente y sus cuentas de Google Ads
    """
    
    def __init__(self):
        # Simulación de datos de cliente_empresas para desarrollo
        # En producción esto vendría de Supabase
        self.empresas_mock = {
            # Empresas para el cliente 'aura'
            "aura": [
                {
                    "id": "empresa-1-uuid",
                    "nombre_nora": "aura", 
                    "nombre_empresa": "LaReina Pasteleria",
                    "giro": "Pastelería",
                    "activo": True
                },
                {
                    "id": "empresa-2-uuid",
                    "nombre_nora": "aura",
                    "nombre_empresa": "Musicando", 
                    "giro": "Música",
                    "activo": True
                },
                {
                    "id": "empresa-3-uuid",
                    "nombre_nora": "aura",
                    "nombre_empresa": "RIMS 2",
                    "giro": "Servicios",
                    "activo": True
                },
                {
                    "id": "empresa-4-uuid",
                    "nombre_nora": "aura",
                    "nombre_empresa": "SAL DE JADE",
                    "giro": "Restaurante",
                    "activo": True
                },
                {
                    "id": "empresa-5-uuid",
                    "nombre_nora": "aura",
                    "nombre_empresa": "Suspiros Cakes",
                    "giro": "Pastelería",
                    "activo": True
                },
                {
                    "id": "empresa-6-uuid",
                    "nombre_nora": "aura",
                    "nombre_empresa": "Suspiros Pastelerías",
                    "giro": "Pastelería", 
                    "activo": True
                },
                {
                    "id": "empresa-7-uuid",
                    "nombre_nora": "aura",
                    "nombre_empresa": "Vetervan",
                    "giro": "Veterinaria",
                    "activo": True
                }
            ]
        }
        
        # Asociaciones de cuentas de Google Ads con empresas
        # google_ads_cuentas_empresas
        self.asociaciones_mock = {
            "3700518858": {"empresa_id": "empresa-1-uuid", "nombre_empresa": "LaReina Pasteleria"},
            "1785583613": {"empresa_id": "empresa-2-uuid", "nombre_empresa": "Musicando"},
            "4890270350": {"empresa_id": "empresa-3-uuid", "nombre_empresa": "RIMS 2"},
            "9737121597": {"empresa_id": "empresa-4-uuid", "nombre_empresa": "SAL DE JADE"},
            "7605115009": {"empresa_id": "empresa-5-uuid", "nombre_empresa": "Suspiros Cakes"},
            "1554994188": {"empresa_id": "empresa-6-uuid", "nombre_empresa": "Suspiros Pastelerías"},
            "5291123262": {"empresa_id": "empresa-7-uuid", "nombre_empresa": "Vetervan"}
        }
    
    def obtener_empresas_disponibles(self, nombre_nora: str) -> List[Dict]:
        """
        Obtiene las empresas del cliente desde cliente_empresas
        """
        if nombre_nora in self.empresas_mock:
            return self.empresas_mock[nombre_nora]
        return []
    
    def obtener_empresa_por_cuenta(self, customer_id: str) -> Optional[Dict]:
        """
        Obtiene la empresa asociada a una cuenta de Google Ads
        desde google_ads_cuentas_empresas
        """
        if customer_id in self.asociaciones_mock:
            asociacion = self.asociaciones_mock[customer_id]
            return {
                "id": asociacion["empresa_id"],
                "nombre": asociacion["nombre_empresa"]
            }
        return None
    
    def asociar_cuenta_empresa(self, customer_id: str, empresa_id: str, nombre_nora: str) -> bool:
        """
        Asocia una cuenta de Google Ads con una empresa específica del cliente
        Actualiza la tabla google_ads_cuentas_empresas
        """
        try:
            # Buscar la empresa en las empresas del cliente
            empresas_cliente = self.obtener_empresas_disponibles(nombre_nora)
            empresa = next((e for e in empresas_cliente if e["id"] == empresa_id), None)
            
            if not empresa:
                logger.error(f"❌ Empresa {empresa_id} no encontrada para cliente {nombre_nora}")
                return False
            
            # Crear o actualizar asociación
            self.asociaciones_mock[customer_id] = {
                "empresa_id": empresa_id,
                "nombre_empresa": empresa["nombre_empresa"]
            }
            
            logger.info(f"✅ Cuenta {customer_id} asociada con empresa {empresa['nombre_empresa']} (ID: {empresa_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error asociando cuenta {customer_id} con empresa {empresa_id}: {e}")
            return False
    
    def obtener_cuentas_por_empresa(self, empresa_id: str) -> List[Dict]:
        """
        Obtiene todas las cuentas de Google Ads asociadas a una empresa
        """
        cuentas = []
        for customer_id, asociacion in self.asociaciones_mock.items():
            if asociacion["empresa_id"] == empresa_id:
                cuentas.append({
                    "customer_id": customer_id,
                    "empresa_id": empresa_id,
                    "empresa_nombre": asociacion["nombre_empresa"]
                })
        return cuentas
    
    def obtener_resumen_por_cliente(self, nombre_nora: str) -> Dict:
        """
        Obtiene un resumen de empresas y cuentas asociadas para un cliente
        """
        empresas = self.obtener_empresas_disponibles(nombre_nora)
        resumen = {
            "cliente": nombre_nora,
            "total_empresas": len(empresas),
            "empresas": []
        }
        
        for empresa in empresas:
            cuentas_empresa = self.obtener_cuentas_por_empresa(empresa["id"])
            resumen["empresas"].append({
                "id": empresa["id"],
                "nombre": empresa["nombre_empresa"],
                "giro": empresa.get("giro", "No especificado"),
                "total_cuentas": len(cuentas_empresa),
                "cuentas": cuentas_empresa
            })
        
        return resumen

# Crear instancia global
empresa_service = EmpresaSimpleService()
