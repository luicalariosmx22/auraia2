#!/usr/bin/env python3
"""
🔄 Gestor de Estados para Conversaciones WhatsApp
Maneja estados pendientes como confirmaciones de tareas, etc.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import threading

class GestorEstados:
    """
    Maneja estados de conversación temporales para usuarios de WhatsApp
    """
    
    def __init__(self):
        self.estados = {}  # {telefono: {estado, datos, timestamp}}
        self.lock = threading.Lock()
        self.timeout_minutos = 10  # Estados expiran en 10 minutos
    
    def establecer_estado(self, telefono: str, tipo_estado: str, datos: Dict) -> None:
        """
        Establece un estado pendiente para un usuario
        """
        with self.lock:
            self.estados[telefono] = {
                "tipo": tipo_estado,
                "datos": datos,
                "timestamp": datetime.now()
            }
            print(f"🔄 Estado establecido para {telefono}: {tipo_estado}")
    
    def obtener_estado(self, telefono: str) -> Optional[Dict]:
        """
        Obtiene el estado actual de un usuario
        """
        with self.lock:
            estado = self.estados.get(telefono)
            
            if estado:
                # Verificar si el estado ha expirado
                tiempo_limite = estado["timestamp"] + timedelta(minutes=self.timeout_minutos)
                if datetime.now() > tiempo_limite:
                    print(f"⏰ Estado expirado para {telefono}, eliminando...")
                    del self.estados[telefono]
                    return None
                
                return estado
            
            return None
    
    def limpiar_estado(self, telefono: str) -> None:
        """
        Limpia el estado de un usuario
        """
        with self.lock:
            if telefono in self.estados:
                del self.estados[telefono]
                print(f"🧹 Estado limpiado para {telefono}")
    
    def limpiar_estados_expirados(self) -> None:
        """
        Limpia estados que han expirado
        """
        with self.lock:
            telefonos_expirados = []
            tiempo_actual = datetime.now()
            
            for telefono, estado in self.estados.items():
                tiempo_limite = estado["timestamp"] + timedelta(minutes=self.timeout_minutos)
                if tiempo_actual > tiempo_limite:
                    telefonos_expirados.append(telefono)
            
            for telefono in telefonos_expirados:
                del self.estados[telefono]
                print(f"🧹 Estado expirado eliminado para {telefono}")
    
    def tiene_estado_pendiente(self, telefono: str, tipo_estado: str = None) -> bool:
        """
        Verifica si un usuario tiene un estado pendiente específico
        """
        estado = self.obtener_estado(telefono)
        if not estado:
            return False
        
        if tipo_estado:
            return estado.get("tipo") == tipo_estado
        
        return True

# Instancia global del gestor de estados
gestor_estados = GestorEstados()

def establecer_confirmacion_tareas(telefono: str, consulta_info: Dict, info_busqueda: Dict) -> None:
    """
    Establece un estado de confirmación pendiente para tareas
    """
    datos = {
        "consulta_info": consulta_info,
        "info_busqueda": info_busqueda
    }
    gestor_estados.establecer_estado(telefono, "confirmacion_tareas", datos)

def obtener_confirmacion_tareas(telefono: str) -> Optional[Dict]:
    """
    Obtiene el estado de confirmación de tareas pendiente
    """
    estado = gestor_estados.obtener_estado(telefono)
    if estado and estado.get("tipo") == "confirmacion_tareas":
        return estado.get("datos")
    return None

def limpiar_confirmacion_tareas(telefono: str) -> None:
    """
    Limpia el estado de confirmación de tareas
    """
    gestor_estados.limpiar_estado(telefono)

def tiene_confirmacion_pendiente(telefono: str) -> bool:
    """
    Verifica si hay una confirmación de tareas pendiente
    """
    return gestor_estados.tiene_estado_pendiente(telefono, "confirmacion_tareas")
