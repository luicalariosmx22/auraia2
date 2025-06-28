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
        
        # Patrones mejorados para mejor extracción de entidades
        patrones_tareas = [
            # Patrones específicos para empresas
            r"tareas?\s+de\s+(?:la\s+)?empresa\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\s+que|\?|$)",
            r"tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)\s+(?:empresa|compañía)",
            r"tareas?\s+(?:activas?\s+)?(?:hay\s+)?(?:en\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)\s+(?:la\s+)?empresa",
            
            # Patrones específicos para usuarios
            r"tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\s+que|\s+tiene|\?|$)",
            r"qué\s+tareas?\s+tiene\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            r"cuáles?\s+son\s+las\s+tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            r"mostrar\s+tareas?\s+(?:de\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            r"ver\s+tareas?\s+(?:de\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            
            # Patrones con filtros integrados
            r"tareas?\s+(pendientes?|completadas?|urgentes?|en\s+proceso)\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            r"(?:tiene|hay)\s+tareas?\s+(?:activas?\s+)?(?:en\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            
            # Patrones para empresas con S.A., Corp, etc.
            r"tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+)\s+(?:s\.a\.|inc|corp|ltd)\.?",
            
            # Patrón genérico (más restrictivo)
            r"tareas?\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]{2,30})(?:\?|$)"
        ]
        
        for patron in patrones_tareas:
            match = re.search(patron, mensaje_lower)
            if match:
                # Extraer entidad y limpiarla
                if len(match.groups()) == 2:  # Patrón con filtro
                    filtro_extra = match.group(1)
                    entidad = match.group(2).strip()
                else:
                    entidad = match.group(1).strip()
                
                # Limpiar la entidad de palabras innecesarias
                entidad = self._limpiar_entidad(entidad)
                
                # Determinar tipo de consulta
                tipo_consulta = self._determinar_tipo_consulta(mensaje_lower, entidad)
                
                return {
                    "es_consulta_tareas": True,
                    "entidad": entidad,
                    "tipo": tipo_consulta,
                    "filtros": self._extraer_filtros(mensaje_lower)
                }
        
        return None
    
    def _limpiar_entidad(self, entidad: str) -> str:
        """Limpia la entidad extraída de palabras innecesarias"""
        # Remover palabras comunes al final
        palabras_remover = [
            "que", "tiene", "hay", "son", "están", "activas", "pendientes",
            "completadas", "urgentes", "vencidas", "empresa", "la empresa"
        ]
        
        entidad_limpia = entidad
        for palabra in palabras_remover:
            # Remover al final
            if entidad_limpia.endswith(" " + palabra):
                entidad_limpia = entidad_limpia[:-len(" " + palabra)]
            # Remover al inicio
            if entidad_limpia.startswith(palabra + " "):
                entidad_limpia = entidad_limpia[len(palabra + " "):]
        
        return entidad_limpia.strip()
    
    def _determinar_tipo_consulta(self, mensaje: str, entidad: str) -> str:
        """Determina si la consulta es por usuario o empresa"""
        
        # Indicadores de consulta por empresa
        indicadores_empresa = [
            "empresa", "compañía", "organización", "negocio", 
            "corporación", "firma", "s.a.", "s.l.", "inc", "ltda",
            "pastelerías", "pastelerias", "cakes", "corp"  # 🆕 Añadimos indicadores específicos
        ]
        
        # Indicadores de consulta por usuario
        indicadores_usuario = [
            "usuario", "empleado", "trabajador", "persona",
            "colaborador", "miembro", "staff", "departamento"
        ]
        
        entidad_lower = entidad.lower()
        mensaje_lower = mensaje.lower()
        
        # 🔥 PRIORIDAD 1: Verificar indicadores explícitos en el mensaje
        if any(ind in mensaje_lower for ind in indicadores_empresa):
            print(f"🏢 Detectado como EMPRESA por indicador en mensaje: {[ind for ind in indicadores_empresa if ind in mensaje_lower]}")
            return "empresa"
            
        if any(ind in mensaje_lower for ind in indicadores_usuario):
            print(f"👤 Detectado como USUARIO por indicador en mensaje: {[ind for ind in indicadores_usuario if ind in mensaje_lower]}")
            return "usuario"
        
        # 🔥 PRIORIDAD 2: Verificar en la entidad misma
        if any(ind in entidad_lower for ind in indicadores_empresa):
            print(f"🏢 Detectado como EMPRESA por indicador en entidad: {[ind for ind in indicadores_empresa if ind in entidad_lower]}")
            return "empresa"
            
        if any(ind in entidad_lower for ind in indicadores_usuario):
            print(f"👤 Detectado como USUARIO por indicador en entidad: {[ind for ind in indicadores_usuario if ind in entidad_lower]}")
            return "usuario"
        
        # 🔥 PRIORIDAD 3: Detectar patrones de nombres típicos
        # Nombres de empresas tienden a tener palabras en mayúscula o términos comerciales
        if any(word in entidad_lower for word in ["suspiros", "tech", "corp", "solutions", "marketing", "group"]):
            print(f"🏢 Detectado como EMPRESA por patrón de nombre comercial")
            return "empresa"
        
        # Nombres de usuarios tienden a ser nombres propios simples
        palabras_entidad = entidad_lower.split()
        if len(palabras_entidad) <= 2 and all(len(palabra) >= 2 for palabra in palabras_entidad):
            # Si son 1-2 palabras cortas, probablemente es un nombre de persona
            nombres_comunes = ["maría", "david", "josé", "luis", "ana", "carlos", "juan", "laura"]
            if any(nombre in entidad_lower for nombre in nombres_comunes):
                print(f"👤 Detectado como USUARIO por nombre común")
                return "usuario"
        
        # 🔥 DEFAULT: Si no está claro, preferir empresa para términos largos o usuario para términos cortos
        if len(entidad.split()) >= 2:
            print(f"🏢 Detectado como EMPRESA por defecto (término largo)")
            return "empresa"
        else:
            print(f"👤 Detectado como USUARIO por defecto (término corto)")
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
    
    def buscar_usuario_por_nombre(self, nombre_usuario: str) -> Tuple[List[Dict], str]:
        """
        Busca usuarios por nombre con diferentes niveles de coincidencia
        Retorna: (usuarios_encontrados, tipo_coincidencia)
        """
        try:
            # 1. Búsqueda exacta
            exacta = supabase.table("usuarios_clientes") \
                .select("id, nombre, correo") \
                .eq("nombre", nombre_usuario) \
                .eq("nombre_nora", self.nombre_nora) \
                .eq("activo", True) \
                .execute()
            
            if exacta.data:
                return exacta.data, "exacta"
            
            # 2. Búsqueda parcial (contiene)
            parcial = supabase.table("usuarios_clientes") \
                .select("id, nombre, correo") \
                .ilike("nombre", f"%{nombre_usuario}%") \
                .eq("nombre_nora", self.nombre_nora) \
                .eq("activo", True) \
                .execute()
            
            if parcial.data:
                return parcial.data, "parcial"
            
            # 3. Búsqueda difusa (por palabras)
            palabras = nombre_usuario.split()
            if len(palabras) > 1:
                usuarios_difusos = []
                for palabra in palabras:
                    if len(palabra) > 2:  # Solo palabras significativas
                        resultado = supabase.table("usuarios_clientes") \
                            .select("id, nombre, correo") \
                            .ilike("nombre", f"%{palabra}%") \
                            .eq("nombre_nora", self.nombre_nora) \
                            .eq("activo", True) \
                            .execute()
                        
                        if resultado.data:
                            usuarios_difusos.extend(resultado.data)
                
                # Eliminar duplicados
                usuarios_unicos = []
                ids_vistos = set()
                for usuario in usuarios_difusos:
                    if usuario["id"] not in ids_vistos:
                        usuarios_unicos.append(usuario)
                        ids_vistos.add(usuario["id"])
                
                if usuarios_unicos:
                    return usuarios_unicos, "difusa"
            
            return [], "sin_coincidencias"
            
        except Exception as e:
            print(f"❌ Error buscando usuario: {e}")
            return [], "error"

    def buscar_empresa_por_nombre(self, nombre_empresa: str) -> Tuple[List[Dict], str]:
        """
        Busca empresas por nombre con diferentes niveles de coincidencia
        Retorna: (empresas_encontradas, tipo_coincidencia)
        """
        try:
            # 1. Búsqueda exacta
            exacta = supabase.table("cliente_empresas") \
                .select("id, nombre_empresa") \
                .eq("nombre_empresa", nombre_empresa) \
                .execute()
            
            if exacta.data:
                return exacta.data, "exacta"
            
            # 2. Búsqueda parcial (contiene)
            parcial = supabase.table("cliente_empresas") \
                .select("id, nombre_empresa") \
                .ilike("nombre_empresa", f"%{nombre_empresa}%") \
                .execute()
            
            if parcial.data:
                return parcial.data, "parcial"
            
            # 3. Búsqueda difusa (por palabras)
            palabras = nombre_empresa.split()
            if len(palabras) > 1:
                empresas_difusas = []
                for palabra in palabras:
                    if len(palabra) > 2:  # Solo palabras significativas
                        resultado = supabase.table("cliente_empresas") \
                            .select("id, nombre_empresa") \
                            .ilike("nombre_empresa", f"%{palabra}%") \
                            .execute()
                        
                        if resultado.data:
                            empresas_difusas.extend(resultado.data)
                
                # Eliminar duplicados
                empresas_unicas = []
                ids_vistos = set()
                for empresa in empresas_difusas:
                    if empresa["id"] not in ids_vistos:
                        empresas_unicas.append(empresa)
                        ids_vistos.add(empresa["id"])
                
                if empresas_unicas:
                    return empresas_unicas, "difusa"
            
            return [], "sin_coincidencias"
            
        except Exception as e:
            print(f"❌ Error buscando empresa: {e}")
            return [], "error"

    def buscar_tareas_por_usuario(self, nombre_usuario: str, filtros: Dict = None) -> Tuple[List[Dict], Dict]:
        """
        Busca tareas asignadas a un usuario específico
        Retorna: (tareas, info_busqueda)
        """
        try:
            usuarios, tipo_coincidencia = self.buscar_usuario_por_nombre(nombre_usuario)
            
            info_busqueda = {
                "usuarios_encontrados": usuarios,
                "tipo_coincidencia": tipo_coincidencia,
                "requiere_confirmacion": False,
                "mensaje_confirmacion": None
            }
            
            if not usuarios:
                return [], info_busqueda
            
            # Si hay múltiples coincidencias, requerir confirmación
            if len(usuarios) > 1:
                info_busqueda["requiere_confirmacion"] = True
                info_busqueda["mensaje_confirmacion"] = self._generar_mensaje_confirmacion_usuario(usuarios, nombre_usuario)
                return [], info_busqueda
            
            # Buscar tareas del usuario único
            usuario_id = usuarios[0]["id"]
            query = supabase.table("tareas") \
                .select("""
                    *,
                    usuarios_clientes!tareas_usuario_empresa_id_fkey(nombre, correo),
                    cliente_empresas!tareas_empresa_id_fkey(nombre_empresa)
                """) \
                .eq("usuario_empresa_id", usuario_id) \
                .eq("nombre_nora", self.nombre_nora) \
                .eq("activo", True)
            
            # Aplicar filtros adicionales
            if filtros:
                query = self._aplicar_filtros(query, filtros)
            
            resultado = query.execute()
            tareas = resultado.data if resultado.data else []
            
            return tareas, info_busqueda
            
        except Exception as e:
            print(f"❌ Error buscando tareas por usuario: {e}")
            return [], {"error": str(e)}
    
    def buscar_tareas_por_empresa(self, nombre_empresa: str, filtros: Dict = None) -> Tuple[List[Dict], Dict]:
        """
        Busca tareas asignadas a una empresa específica
        Retorna: (tareas, info_busqueda)
        """
        try:
            empresas, tipo_coincidencia = self.buscar_empresa_por_nombre(nombre_empresa)
            
            info_busqueda = {
                "empresas_encontradas": empresas,
                "tipo_coincidencia": tipo_coincidencia,
                "requiere_confirmacion": False,
                "mensaje_confirmacion": None
            }
            
            if not empresas:
                return [], info_busqueda
            
            # Si hay múltiples coincidencias, requerir confirmación
            if len(empresas) > 1:
                info_busqueda["requiere_confirmacion"] = True
                info_busqueda["mensaje_confirmacion"] = self._generar_mensaje_confirmacion_empresa(empresas, nombre_empresa)
                return [], info_busqueda
            
            # Buscar tareas de la empresa única
            empresa_id = empresas[0]["id"]
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
            tareas = resultado.data if resultado.data else []
            
            return tareas, info_busqueda
            
        except Exception as e:
            print(f"❌ Error buscando tareas por empresa: {e}")
            return [], {"error": str(e)}
    
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
    
    def formatear_respuesta_tareas(self, tareas: List[Dict], consulta_info: Dict, info_busqueda: Dict = None) -> str:
        """
        Formatea la respuesta sobre tareas para el usuario
        """
        # Si hay un mensaje de confirmación pendiente, retornarlo
        if info_busqueda and info_busqueda.get("requiere_confirmacion"):
            return info_busqueda.get("mensaje_confirmacion", "")
        
        # Si no se encontraron entidades
        if info_busqueda and not info_busqueda.get("usuarios_encontrados", []) and not info_busqueda.get("empresas_encontradas", []):
            entidad = consulta_info.get("entidad", "la entidad solicitada")
            tipo = consulta_info.get("tipo", "usuario")
            
            mensaje = f"🔍 No encontré ningún **{tipo}** que coincida con **{entidad}**.\n\n"
            mensaje += "💡 **Sugerencias:**\n"
            mensaje += "• Verifica la ortografía\n"
            mensaje += "• Intenta con un nombre más específico\n"
            mensaje += "• Usa solo el nombre o apellido\n"
            
            if tipo == "usuario":
                mensaje += "• Pregunta por tareas de una empresa específica\n"
            else:
                mensaje += "• Pregunta por tareas de un usuario específico\n"
            
            return mensaje
        
        if not tareas:
            entidad = consulta_info.get("entidad", "la entidad solicitada")
            tipo_busqueda = info_busqueda.get("tipo_coincidencia", "")
            
            if info_busqueda:
                usuarios = info_busqueda.get("usuarios_encontrados", [])
                empresas = info_busqueda.get("empresas_encontradas", [])
                
                if usuarios:
                    entidad_real = usuarios[0].get("nombre", entidad)
                elif empresas:
                    entidad_real = empresas[0].get("nombre_empresa", entidad)
                else:
                    entidad_real = entidad
            else:
                entidad_real = entidad
            
            mensaje = f"🔍 No encontré tareas activas para **{entidad_real}** en este momento.\n\n"
            
            if tipo_busqueda == "parcial" or tipo_busqueda == "difusa":
                mensaje += f"✅ Encontré el registro, pero no tiene tareas asignadas.\n\n"
            
            mensaje += "¿Te gustaría que busque con otros criterios o necesitas crear una nueva tarea?"
            return mensaje
        
        # Contar tareas por estatus
        conteo_estatus = {}
        for tarea in tareas:
            estatus = tarea.get("estatus", "sin_estatus")
            conteo_estatus[estatus] = conteo_estatus.get(estatus, 0) + 1
        
        # Determinar el nombre real de la entidad
        entidad_real = consulta_info.get("entidad", "")
        if info_busqueda:
            usuarios = info_busqueda.get("usuarios_encontrados", [])
            empresas = info_busqueda.get("empresas_encontradas", [])
            
            if usuarios:
                entidad_real = usuarios[0].get("nombre", entidad_real)
            elif empresas:
                entidad_real = empresas[0].get("nombre_empresa", entidad_real)
        
        tipo = consulta_info.get("tipo", "usuario")
        
        # Encabezado
        respuesta = f"📋 **Tareas de {entidad_real}** ({tipo}):\n\n"
        
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
    
    def _generar_mensaje_confirmacion_usuario(self, usuarios: List[Dict], nombre_buscado: str) -> str:
        """Genera mensaje de confirmación cuando hay múltiples usuarios"""
        mensaje = f"🤔 Encontré {len(usuarios)} usuarios que podrían coincidir con **{nombre_buscado}**:\n\n"
        
        for i, usuario in enumerate(usuarios[:5], 1):  # Máximo 5 opciones
            nombre = usuario.get("nombre", "Sin nombre")
            correo = usuario.get("correo", "Sin correo")
            mensaje += f"{i}. **{nombre}**"
            if correo:
                mensaje += f" ({correo})"
            mensaje += "\n"
        
        if len(usuarios) > 5:
            mensaje += f"... y {len(usuarios) - 5} más.\n"
        
        mensaje += "\n¿Podrías especificar a cuál te refieres? Puedes responder con el número o el nombre completo."
        return mensaje

    def _generar_mensaje_confirmacion_empresa(self, empresas: List[Dict], nombre_buscado: str) -> str:
        """Genera mensaje de confirmación cuando hay múltiples empresas"""
        mensaje = f"🤔 Encontré {len(empresas)} empresas que podrían coincidir con **{nombre_buscado}**:\n\n"
        
        for i, empresa in enumerate(empresas[:5], 1):  # Máximo 5 opciones
            nombre = empresa.get("nombre_empresa", "Sin nombre")
            mensaje += f"{i}. **{nombre}**\n"
        
        if len(empresas) > 5:
            mensaje += f"... y {len(empresas) - 5} más.\n"
        
        mensaje += "\n¿Podrías especificar a cuál te refieres? Puedes responder con el número o el nombre completo."
        return mensaje

    def procesar_confirmacion_usuario(self, respuesta: str, usuarios_opciones: List[Dict]) -> Optional[Dict]:
        """
        Procesa la respuesta de confirmación del usuario para seleccionar un usuario específico
        """
        respuesta_limpia = respuesta.strip().lower()
        
        # Intentar por número
        try:
            numero = int(respuesta_limpia)
            if 1 <= numero <= len(usuarios_opciones):
                return usuarios_opciones[numero - 1]
        except ValueError:
            pass
        
        # Intentar por nombre
        for usuario in usuarios_opciones:
            nombre_usuario = usuario.get("nombre", "").lower()
            if respuesta_limpia in nombre_usuario or nombre_usuario in respuesta_limpia:
                return usuario
        
        return None

    def procesar_confirmacion_empresa(self, respuesta: str, empresas_opciones: List[Dict]) -> Optional[Dict]:
        """
        Procesa la respuesta de confirmación del usuario para seleccionar una empresa específica
        """
        respuesta_limpia = respuesta.strip().lower()
        
        # Intentar por número
        try:
            numero = int(respuesta_limpia)
            if 1 <= numero <= len(empresas_opciones):
                return empresas_opciones[numero - 1]
        except ValueError:
            pass
        
        # Intentar por nombre
        for empresa in empresas_opciones:
            nombre_empresa = empresa.get("nombre_empresa", "").lower()
            if respuesta_limpia in nombre_empresa or nombre_empresa in respuesta_limpia:
                return empresa
        
        return None

def procesar_consulta_tareas(mensaje: str, usuario: Dict, telefono: str = None, nombre_nora: str = "aura") -> Optional[str]:
    """
    Función principal para procesar consultas de tareas desde la IA
    """
    from clientes.aura.utils.gestor_estados import tiene_confirmacion_pendiente, establecer_confirmacion_tareas
    
    try:
        # Si hay una confirmación pendiente, procesarla primero
        if telefono and tiene_confirmacion_pendiente(telefono):
            return procesar_confirmacion_tareas(mensaje, telefono, usuario, nombre_nora)
        
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
        info_busqueda = {}
        
        if consulta_info["tipo"] == "empresa":
            tareas, info_busqueda = consultor.buscar_tareas_por_empresa(
                consulta_info["entidad"], 
                consulta_info["filtros"]
            )
        else:  # usuario
            tareas, info_busqueda = consultor.buscar_tareas_por_usuario(
                consulta_info["entidad"],
                consulta_info["filtros"]
            )
        
        # Si requiere confirmación, establecer estado y retornar mensaje
        if info_busqueda.get("requiere_confirmacion") and telefono:
            establecer_confirmacion_tareas(telefono, consulta_info, info_busqueda)
            return info_busqueda.get("mensaje_confirmacion", "Por favor, especifica cuál opción prefieres.")
        
        # Formatear y retornar respuesta
        return consultor.formatear_respuesta_tareas(tareas, consulta_info, info_busqueda)
        
    except Exception as e:
        print(f"❌ Error procesando consulta de tareas: {e}")
        return "❌ Ocurrió un error al consultar las tareas. Por favor, intenta nuevamente."

def procesar_confirmacion_tareas(mensaje: str, telefono: str, usuario: Dict, nombre_nora: str = "aura") -> Optional[str]:
    """
    Procesa una respuesta de confirmación para búsqueda de tareas
    """
    from clientes.aura.utils.gestor_estados import obtener_confirmacion_tareas, limpiar_confirmacion_tareas
    
    try:
        # Obtener datos de confirmación pendiente
        datos_confirmacion = obtener_confirmacion_tareas(telefono)
        if not datos_confirmacion:
            return None  # No hay confirmación pendiente
        
        consulta_info = datos_confirmacion.get("consulta_info", {})
        info_busqueda = datos_confirmacion.get("info_busqueda", {})
        
        consultor = ConsultorTareas(usuario, nombre_nora)
        
        entidad_seleccionada = None
        
        # Procesar según el tipo de consulta
        if consulta_info.get("tipo") == "empresa":
            empresas_opciones = info_busqueda.get("empresas_encontradas", [])
            entidad_seleccionada = consultor.procesar_confirmacion_empresa(mensaje, empresas_opciones)
        else:  # usuario
            usuarios_opciones = info_busqueda.get("usuarios_encontrados", [])
            entidad_seleccionada = consultor.procesar_confirmacion_usuario(mensaje, usuarios_opciones)
        
        # Limpiar estado de confirmación
        limpiar_confirmacion_tareas(telefono)
        
        if not entidad_seleccionada:
            return "❌ No pude identificar la opción seleccionada. Por favor, intenta de nuevo con el número o nombre completo."
        
        # Buscar tareas de la entidad seleccionada
        tareas = []
        if consulta_info.get("tipo") == "empresa":
            query = supabase.table("tareas") \
                .select("""
                    *,
                    usuarios_clientes!tareas_usuario_empresa_id_fkey(nombre, correo),
                    cliente_empresas!tareas_empresa_id_fkey(nombre_empresa)
                """) \
                .eq("empresa_id", entidad_seleccionada["id"]) \
                .eq("nombre_nora", nombre_nora) \
                .eq("activo", True)
            
            if consulta_info.get("filtros"):
                query = consultor._aplicar_filtros(query, consulta_info["filtros"])
            
            resultado = query.execute()
            tareas = resultado.data if resultado.data else []
            
            # Actualizar info para el formateo
            info_busqueda_actualizada = {
                "empresas_encontradas": [entidad_seleccionada],
                "tipo_coincidencia": "confirmada",
                "requiere_confirmacion": False
            }
        else:  # usuario
            query = supabase.table("tareas") \
                .select("""
                    *,
                    usuarios_clientes!tareas_usuario_empresa_id_fkey(nombre, correo),
                    cliente_empresas!tareas_empresa_id_fkey(nombre_empresa)
                """) \
                .eq("usuario_empresa_id", entidad_seleccionada["id"]) \
                .eq("nombre_nora", nombre_nora) \
                .eq("activo", True)
            
            if consulta_info.get("filtros"):
                query = consultor._aplicar_filtros(query, consulta_info["filtros"])
            
            resultado = query.execute()
            tareas = resultado.data if resultado.data else []
            
            # Actualizar info para el formateo
            info_busqueda_actualizada = {
                "usuarios_encontrados": [entidad_seleccionada],
                "tipo_coincidencia": "confirmada",
                "requiere_confirmacion": False
            }
        
        # Formatear y retornar respuesta
        return consultor.formatear_respuesta_tareas(tareas, consulta_info, info_busqueda_actualizada)
        
    except Exception as e:
        print(f"❌ Error procesando confirmación de tareas: {e}")
        limpiar_confirmacion_tareas(telefono)
        return "❌ Ocurrió un error procesando tu selección. Por favor, intenta de nuevo."
