#!/usr/bin/env python3
"""
🎯 Detector de Intenciones para WhatsApp
Detecta cuando el usuario quiere realizar acciones específicas como crear tareas
"""

import re
from typing import Dict, Optional, List
from clientes.aura.auth.privilegios import PrivilegiosManager


class DetectorIntenciones:
    """Detecta intenciones del usuario en mensajes de WhatsApp"""
    
    def __init__(self):
        # Patrones para detectar intención de crear tareas
        self.patrones_crear_tarea = [
            r'(?i)\b(crear|nueva|agregar|registrar|anotar)\s+(tarea|task|pendiente|actividad)\b',
            r'(?i)\b(quiero|necesito|voy a)\s+crear\s+una\s+tarea\b',
            r'(?i)\b(agregar|crear)\s+una\s+(nueva\s+)?tarea\b',
            r'(?i)\b(nueva\s+)?(tarea|task|pendiente)\b',
            r'(?i)\b(tengo\s+una\s+tarea|hay\s+que\s+hacer)\b',
            r'(?i)\b(asignar\s+tarea|tarea\s+para)\b',
            r'(?i)\b(recordar|anotar)\s+(que|de)\s+\w+',
            r'(?i)\b(hay\s+que|necesito\s+que|quiero\s+que)\s+\w+',
            r'(?i)\b(tarea\s+nueva|nueva\s+actividad)\b'
        ]
        
        # Patrones para detectar intención de consultar tareas
        self.patrones_consultar_tareas = [
            r'(?i)\b(ver|mostrar|consultar|listar)\s+(mis\s+)?tareas\b',
            r'(?i)\b(que\s+tareas|cuales\s+tareas|mis\s+tareas)\b',
            r'(?i)\b(pendientes|por\s+hacer|vencidas)\b',
            r'(?i)\b(tareas\s+(de|del|para))\s+\w+',
            r'(?i)\b(estado\s+de\s+tareas|reporte\s+de\s+tareas)\b'
        ]
        
        # Patrones para cancelar acciones
        self.patrones_cancelar = [
            r'(?i)\b(cancelar|salir|terminar|parar|stop)\b',
            r'(?i)\b(no\s+quiero|ya\s+no|olvídalo)\b',
            r'(?i)\b(mejor\s+después|otro\s+momento)\b'
        ]
        
        # Patrones para confirmar acciones
        self.patrones_confirmar = [
            r'(?i)\b(si|sí|yes|ok|okay|dale|confirmar|correcto)\b',
            r'(?i)\b(así\s+es|exacto|perfecto|adelante)\b'
        ]
    
    def detectar_intencion_principal(self, mensaje: str, usuario_datos: Dict) -> Optional[str]:
        """
        Detecta la intención principal del mensaje del usuario
        Retorna: 'crear_tarea', 'consultar_tareas', 'cancelar', 'confirmar', o None
        """
        mensaje_limpio = mensaje.strip()
        
        # Verificar privilegios para crear tareas usando PrivilegiosManager
        manager = PrivilegiosManager(usuario_datos)
        puede_crear_tareas = manager.puede_acceder("tareas", "write")
        
        # Detectar intención de crear tarea
        if puede_crear_tareas:
            for patron in self.patrones_crear_tarea:
                if re.search(patron, mensaje_limpio):
                    return "crear_tarea"
        
        # Detectar intención de consultar tareas
        for patron in self.patrones_consultar_tareas:
            if re.search(patron, mensaje_limpio):
                return "consultar_tareas"
        
        # Detectar cancelación
        for patron in self.patrones_cancelar:
            if re.search(patron, mensaje_limpio):
                return "cancelar"
        
        # Detectar confirmación
        for patron in self.patrones_confirmar:
            if re.search(patron, mensaje_limpio):
                return "confirmar"
        
        return None
    
    def es_mensaje_crear_tarea(self, mensaje: str, usuario_datos: Dict) -> bool:
        """Verifica específicamente si el mensaje indica intención de crear tarea"""
        return self.detectar_intencion_principal(mensaje, usuario_datos) == "crear_tarea"
    
    def es_mensaje_consultar_tareas(self, mensaje: str, usuario_datos: Dict) -> bool:
        """Verifica específicamente si el mensaje indica intención de consultar tareas"""
        return self.detectar_intencion_principal(mensaje, usuario_datos) == "consultar_tareas"
    
    def es_mensaje_cancelar(self, mensaje: str) -> bool:
        """Verifica si el mensaje indica intención de cancelar"""
        return self.detectar_intencion_principal(mensaje, {}) == "cancelar"
    
    def es_mensaje_confirmar(self, mensaje: str) -> bool:
        """Verifica si el mensaje indica intención de confirmar"""
        return self.detectar_intencion_principal(mensaje, {}) == "confirmar"
    
    def extraer_contexto_tarea(self, mensaje: str) -> Dict:
        """
        Extrae información contextual del mensaje cuando quiere crear una tarea
        """
        contexto = {}
        
        # Buscar posible título de tarea en el mensaje
        patrones_titulo = [
            r'(?i)crear\s+tarea\s+["\']([^"\']+)["\']',
            r'(?i)nueva\s+tarea\s+["\']([^"\']+)["\']',
            r'(?i)tarea\s+["\']([^"\']+)["\']',
            r'(?i)(?:crear|nueva|agregar)\s+tarea\s+(.+)',
            r'(?i)tarea\s+para\s+(.+)',
            r'(?i)necesito\s+(.+)',
            r'(?i)hay\s+que\s+(.+)',
            r'(?i)recordar\s+(.+)'
        ]
        
        for patron in patrones_titulo:
            match = re.search(patron, mensaje.strip())
            if match:
                titulo_candidato = match.group(1).strip()
                # Limpiar título (remover palabras comunes al final)
                titulo_candidato = re.sub(r'\s+(por\s+favor|please|urgente|prioridad\s+alta)$', '', titulo_candidato, flags=re.IGNORECASE)
                if len(titulo_candidato) > 3:  # Debe tener contenido real
                    contexto["titulo_sugerido"] = titulo_candidato
                    break
        
        # Buscar menciones de prioridad
        if re.search(r'(?i)\b(urgente|prioridad\s+alta|crítico|importante)\b', mensaje):
            contexto["prioridad_sugerida"] = "alta"
        elif re.search(r'(?i)\b(no\s+urgente|prioridad\s+baja|cuando\s+puedas)\b', mensaje):
            contexto["prioridad_sugerida"] = "baja"
        
        # Buscar menciones de tiempo/fecha
        patrones_fecha = [
            r'(?i)\b(hoy|today)\b',
            r'(?i)\b(mañana|tomorrow)\b',
            r'(?i)\b(esta\s+semana|this\s+week)\b',
            r'(?i)\b(próxima\s+semana|next\s+week)\b',
            r'(?i)\b(urgente|asap)\b'
        ]
        
        for patron in patrones_fecha:
            if re.search(patron, mensaje):
                contexto["fecha_sugerida"] = re.search(patron, mensaje).group(0).lower()
                break
        
        # Buscar menciones de personas
        patrones_persona = [
            r'(?i)\bpara\s+([A-Za-z\s]+)\b',
            r'(?i)\basignar\s+a\s+([A-Za-z\s]+)\b',
            r'(?i)\bque\s+([A-Za-z\s]+)\s+haga\b'
        ]
        
        for patron in patrones_persona:
            match = re.search(patron, mensaje)
            if match:
                persona = match.group(1).strip()
                if len(persona) > 2 and not re.search(r'(?i)\b(hacer|ver|crear|todo|empresa)\b', persona):
                    contexto["persona_sugerida"] = persona
                    break
        
        return contexto
    
    def generar_mensaje_bienvenida_tarea(self, contexto: Dict) -> str:
        """Genera un mensaje de bienvenida personalizado para crear tarea"""
        mensaje = "🎯 **¡Perfecto! Te ayudo a crear una nueva tarea.**\n\n"
        
        if contexto.get("titulo_sugerido"):
            mensaje += f"📝 Veo que quieres crear: *{contexto['titulo_sugerido']}*\n"
            mensaje += "Te guiaré paso a paso para completar los detalles.\n\n"
        else:
            mensaje += "Te guiaré paso a paso para recopilar toda la información necesaria.\n\n"
        
        if contexto.get("prioridad_sugerida"):
            mensaje += f"🎯 Prioridad detectada: *{contexto['prioridad_sugerida'].capitalize()}*\n"
        
        if contexto.get("fecha_sugerida"):
            mensaje += f"📅 Fecha mencionada: *{contexto['fecha_sugerida']}*\n"
        
        if contexto.get("persona_sugerida"):
            mensaje += f"👤 Persona mencionada: *{contexto['persona_sugerida']}*\n"
        
        if any(contexto.get(k) for k in ["prioridad_sugerida", "fecha_sugerida", "persona_sugerida"]):
            mensaje += "\n💡 *Confirmaré esta información durante el proceso.*\n"
        
        mensaje += "\n🚀 ¡Comencemos!"
        
        return mensaje

# Instancia global del detector
detector_intenciones = DetectorIntenciones()
