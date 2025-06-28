#!/usr/bin/env python3
"""
📋 Módulo de Consultas de Tareas para Nora AI
Permite consultar tareas por usuario, empresa, estatus, etc.
"""

from typing import Dict, List, Optional, Tuple
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager
from datetime import datetime, date
import re

class ConsultorTareas:
    """
    Maneja las consultas de tareas para el sistema de IA
    """
    
    def __init__(self, usuario_consultor: Dict, nombre_nora: str = "aura"):
        """
        Inicializa el consultor con los datos del usuario que hace la consulta
        """
        self.usuario_consultor = usuario_consultor
        self.nombre_nora = nombre_nora
        self.privilegios = PrivilegiosManager(usuario_consultor)
        
    def puede_consultar_tareas(self) -> bool:
        """Verifica si el usuario puede consultar tareas"""
        return self.privilegios.puede_acceder("tareas", "read")
    
    def detectar_consulta_tareas(self, mensaje: str) -> Optional[Dict]:
        """
        Detecta si el mensaje es una consulta sobre tareas y extrae parámetros
        """
        mensaje_lower = mensaje.lower().strip()
        
        # Patrones de detección de consultas de tareas
        patrones_tareas = [
            r"tareas?\s+de\s+(.+)",
            r"qué\s+tareas?\s+tiene\s+(.+)",
            r"cuáles?\s+son\s+las\s+tareas?\s+de\s+(.+)",
            r"mostrar\s+tareas?\s+de\s+(.+)",
            r"ver\s+tareas?\s+de\s+(.+)",
            r"consultar\s+tareas?\s+de\s+(.+)",
            r"listar\s+tareas?\s+de\s+(.+)",
            r"tareas?\s+(.+)",
            r"pendientes\s+de\s+(.+)",
            r"(.+)\s+tiene\s+tareas?",
            r"tareas?\s+pendientes?\s+(.+)",
            r"tareas?\s+urgentes?\s+(.+)"
        ]
        
        for patron in patrones_tareas:
            match = re.search(patron, mensaje_lower)
            if match:
                entidad = match.group(1).strip()
                
                # Determinar tipo de consulta
                tipo_consulta = self._determinar_tipo_consulta(mensaje_lower, entidad)
                
                return {
                    "es_consulta_tareas": True,
                    "entidad": entidad,
                    "tipo": tipo_consulta,
                    "filtros": self._extraer_filtros(mensaje_lower)
                }
        
        return None
    
    def _determinar_tipo_consulta(self, mensaje: str, entidad: str) -> str:
        """Determina si la consulta es por usuario o empresa"""
        
        # Indicadores de consulta por empresa
        indicadores_empresa = [
            "empresa", "compañía", "organización", "negocio", 
            "corporación", "firma", "s.a.", "s.l.", "inc", "ltda"
        ]
        
        # Indicadores de consulta por usuario
        indicadores_usuario = [
            "usuario", "empleado", "trabajador", "persona",
            "colaborador", "miembro", "staff"
        ]
        
        entidad_lower = entidad.lower()
        mensaje_lower = mensaje.lower()
        
        # Verificar indicadores explícitos
        if any(ind in mensaje_lower for ind in indicadores_empresa):
            return "empresa"
        if any(ind in mensaje_lower for ind in indicadores_usuario):
            return "usuario"
        
        # Verificar en la entidad misma
        if any(ind in entidad_lower for ind in indicadores_empresa):
            return "empresa"
        
        # Por defecto, asumir que es usuario si no hay indicadores claros
        return "usuario"
    
    def _extraer_filtros(self, mensaje: str) -> Dict:
        """Extrae filtros adicionales del mensaje"""
        filtros = {}
        
        # Filtros de estatus
        if "pendiente" in mensaje:
            filtros["estatus"] = "pendiente"
        elif "completada" in mensaje or "terminada" in mensaje:
            filtros["estatus"] = "completada"
        elif "en proceso" in mensaje or "progreso" in mensaje:
            filtros["estatus"] = "en_proceso"
        
        # Filtros de prioridad
        if "urgente" in mensaje or "alta" in mensaje:
            filtros["prioridad"] = "alta"
        elif "baja" in mensaje:
            filtros["prioridad"] = "baja"
        
        # Filtros de tiempo
        if "hoy" in mensaje:
            filtros["fecha"] = "hoy"
        elif "esta semana" in mensaje or "semana" in mensaje:
            filtros["fecha"] = "semana"
        elif "vencida" in mensaje or "atrasada" in mensaje:
            filtros["fecha"] = "vencidas"
        
        return filtros
    
    def buscar_tareas_por_usuario(self, nombre_usuario: str, filtros: Dict = None) -> List[Dict]:
        """
        Busca tareas asignadas a un usuario específico
        """
        try:
            # Construir consulta base
            query = supabase.table("tareas") \
                .select("""
                    *,
                    usuarios_clientes!tareas_usuario_empresa_id_fkey(nombre, correo),
                    cliente_empresas!tareas_empresa_id_fkey(nombre_empresa)
                """) \
                .eq("nombre_nora", self.nombre_nora) \
                .eq("activo", True)
            
            # Buscar usuario por nombre (búsqueda flexible)
            usuario_resultado = supabase.table("usuarios_clientes") \
                .select("id, nombre") \
                .ilike("nombre", f"%{nombre_usuario}%") \
                .eq("nombre_nora", self.nombre_nora) \
                .eq("activo", True) \
                .execute()
            
            if not usuario_resultado.data:
                return []
            
            usuario_id = usuario_resultado.data[0]["id"]
            query = query.eq("usuario_empresa_id", usuario_id)
            
            # Aplicar filtros adicionales
            if filtros:
                query = self._aplicar_filtros(query, filtros)
            
            resultado = query.execute()
            return resultado.data if resultado.data else []
            
        except Exception as e:
            print(f"❌ Error buscando tareas por usuario: {e}")
            return []
    
    def buscar_tareas_por_empresa(self, nombre_empresa: str, filtros: Dict = None) -> List[Dict]:
        """
        Busca tareas asignadas a una empresa específica
        """
        try:
            # Buscar empresa por nombre
            empresa_resultado = supabase.table("cliente_empresas") \
                .select("id, nombre_empresa") \
                .ilike("nombre_empresa", f"%{nombre_empresa}%") \
                .execute()
            
            if not empresa_resultado.data:
                return []
            
            empresa_id = empresa_resultado.data[0]["id"]
            
            # Construir consulta
            query = supabase.table("tareas") \
                .select("""
                    *,
                    usuarios_clientes!tareas_usuario_empresa_id_fkey(nombre, correo),
                    cliente_empresas!tareas_empresa_id_fkey(nombre_empresa)
                """) \
                .eq("empresa_id", empresa_id) \
                .eq("nombre_nora", self.nombre_nora) \
                .eq("activo", True)
            
            # Aplicar filtros adicionales
            if filtros:
                query = self._aplicar_filtros(query, filtros)
            
            resultado = query.execute()
            return resultado.data if resultado.data else []
            
        except Exception as e:
            print(f"❌ Error buscando tareas por empresa: {e}")
            return []
    
    def _aplicar_filtros(self, query, filtros: Dict):
        """Aplica filtros adicionales a la consulta"""
        
        if "estatus" in filtros:
            query = query.eq("estatus", filtros["estatus"])
        
        if "prioridad" in filtros:
            query = query.eq("prioridad", filtros["prioridad"])
        
        if "fecha" in filtros:
            hoy = date.today()
            if filtros["fecha"] == "hoy":
                query = query.eq("fecha_limite", hoy)
            elif filtros["fecha"] == "vencidas":
                query = query.lt("fecha_limite", hoy)
            elif filtros["fecha"] == "semana":
                from datetime import timedelta
                fin_semana = hoy + timedelta(days=7)
                query = query.gte("fecha_limite", hoy).lte("fecha_limite", fin_semana)
        
        return query
    
    def formatear_respuesta_tareas(self, tareas: List[Dict], consulta_info: Dict) -> str:
        """
        Formatea la respuesta sobre tareas para el usuario
        """
        if not tareas:
            entidad = consulta_info.get("entidad", "la entidad solicitada")
            return f"🔍 No encontré tareas activas para **{entidad}** en este momento.\n\n¿Te gustaría que busque con otros criterios o necesitas crear una nueva tarea?"
        
        # Contar tareas por estatus
        conteo_estatus = {}
        for tarea in tareas:
            estatus = tarea.get("estatus", "sin_estatus")
            conteo_estatus[estatus] = conteo_estatus.get(estatus, 0) + 1
        
        entidad = consulta_info.get("entidad", "")
        tipo = consulta_info.get("tipo", "usuario")
        
        # Encabezado
        respuesta = f"📋 **Tareas de {entidad}** ({tipo}):\n\n"
        
        # Resumen por estatus
        respuesta += "📊 **Resumen:**\n"
        for estatus, cantidad in conteo_estatus.items():
            emoji = self._get_emoji_estatus(estatus)
            respuesta += f"{emoji} {estatus.replace('_', ' ').title()}: {cantidad}\n"
        
        respuesta += f"\n**Total: {len(tareas)} tareas**\n\n"
        
        # Detalles de tareas (máximo 10 para no sobrecargar)
        respuesta += "📝 **Detalles:**\n"
        for i, tarea in enumerate(tareas[:10], 1):
            titulo = tarea.get("titulo", "Sin título")
            estatus = tarea.get("estatus", "pendiente")
            prioridad = tarea.get("prioridad", "media")
            fecha_limite = tarea.get("fecha_limite")
            
            emoji_estatus = self._get_emoji_estatus(estatus)
            emoji_prioridad = self._get_emoji_prioridad(prioridad)
            
            respuesta += f"{i}. {emoji_estatus} **{titulo}**\n"
            respuesta += f"   └ {emoji_prioridad} Prioridad: {prioridad.title()}"
            
            if fecha_limite:
                fecha_str = self._formatear_fecha(fecha_limite)
                respuesta += f" | 📅 {fecha_str}"
            
            respuesta += "\n\n"
        
        # Nota si hay más tareas
        if len(tareas) > 10:
            respuesta += f"... y {len(tareas) - 10} tareas más.\n\n"
        
        # Sugerencias de acciones
        respuesta += "💡 **¿Qué puedo hacer por ti?**\n"
        respuesta += "• Filtrar por estatus específico\n"
        respuesta += "• Ver tareas urgentes\n"
        respuesta += "• Buscar por empresa\n"
        respuesta += "• Crear una nueva tarea"
        
        return respuesta
    
    def _get_emoji_estatus(self, estatus: str) -> str:
        """Retorna emoji según el estatus"""
        emojis = {
            "pendiente": "⏳",
            "en_proceso": "🔄",
            "completada": "✅",
            "cancelada": "❌",
            "pausada": "⏸️"
        }
        return emojis.get(estatus, "📝")
    
    def _get_emoji_prioridad(self, prioridad: str) -> str:
        """Retorna emoji según la prioridad"""
        emojis = {
            "alta": "🔴",
            "media": "🟡",
            "baja": "🟢"
        }
        return emojis.get(prioridad, "⚪")
    
    def _formatear_fecha(self, fecha) -> str:
        """Formatea fecha para mostrar al usuario"""
        if isinstance(fecha, str):
            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            except:
                return fecha
        else:
            fecha_obj = fecha
        
        hoy = date.today()
        diff = (fecha_obj - hoy).days
        
        if diff < 0:
            return f"Vencida ({abs(diff)} días)"
        elif diff == 0:
            return "Hoy ⚠️"
        elif diff == 1:
            return "Mañana"
        elif diff <= 7:
            return f"En {diff} días"
        else:
            return fecha_obj.strftime("%d/%m/%Y")

def procesar_consulta_tareas(mensaje: str, usuario: Dict, nombre_nora: str = "aura") -> Optional[str]:
    """
    Función principal para procesar consultas de tareas desde la IA
    """
    try:
        consultor = ConsultorTareas(usuario, nombre_nora)
        
        # Verificar permisos
        if not consultor.puede_consultar_tareas():
            return "❌ No tienes permisos para consultar tareas del sistema."
        
        # Detectar si es una consulta de tareas
        consulta_info = consultor.detectar_consulta_tareas(mensaje)
        if not consulta_info:
            return None  # No es una consulta de tareas
        
        print(f"🔍 Consulta de tareas detectada: {consulta_info}")
        
        # Buscar tareas según el tipo
        tareas = []
        if consulta_info["tipo"] == "empresa":
            tareas = consultor.buscar_tareas_por_empresa(
                consulta_info["entidad"], 
                consulta_info["filtros"]
            )
        else:  # usuario
            tareas = consultor.buscar_tareas_por_usuario(
                consulta_info["entidad"],
                consulta_info["filtros"]
            )
        
        # Formatear y retornar respuesta
        return consultor.formatear_respuesta_tareas(tareas, consulta_info)
        
    except Exception as e:
        print(f"❌ Error procesando consulta de tareas: {e}")
        return "❌ Ocurrió un error al consultar las tareas. Por favor, intenta nuevamente."
