#!/usr/bin/env python3
"""
📝 Sistema de Formularios Conversacionales
Maneja la creación de tareas y otros datos paso a paso vía WhatsApp
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import uuid
from clientes.aura.utils.gestor_estados import gestor_estados
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager


class PasoFormulario:
    """Representa un paso individual del formulario"""
    
    def __init__(self, campo: str, pregunta: str, validador: Callable = None, 
                 opciones: List[str] = None, obligatorio: bool = True,
                 depende_de: str = None, condicion_dependencia: Callable = None):
        self.campo = campo
        self.pregunta = pregunta
        self.validador = validador
        self.opciones = opciones
        self.obligatorio = obligatorio
        self.depende_de = depende_de
        self.condicion_dependencia = condicion_dependencia


class FormularioConversacional:
    """Maneja formularios paso a paso via conversación"""
    
    def __init__(self, tipo_formulario: str, pasos: List[PasoFormulario], 
                 callback_completar: Callable, usuario_datos: Dict):
        self.tipo_formulario = tipo_formulario
        self.pasos = pasos
        self.callback_completar = callback_completar
        self.usuario_datos = usuario_datos
    
    def iniciar_formulario(self, telefono: str) -> str:
        """Inicia el formulario y devuelve la primera pregunta"""
        datos_formulario = {
            "tipo": self.tipo_formulario,
            "paso_actual": 0,
            "respuestas": {},
            "usuario_datos": self.usuario_datos,
            "pasos": [{"campo": p.campo, "pregunta": p.pregunta, 
                      "opciones": p.opciones, "obligatorio": p.obligatorio,
                      "depende_de": p.depende_de} for p in self.pasos],
            "callback": "completar_creacion_tarea"
        }
        
        gestor_estados.establecer_estado(telefono, f"formulario_{self.tipo_formulario}", datos_formulario)
        
        primer_paso = self._obtener_siguiente_paso_valido(datos_formulario, -1)
        if primer_paso is not None:
            datos_formulario["paso_actual"] = primer_paso
            gestor_estados.establecer_estado(telefono, f"formulario_{self.tipo_formulario}", datos_formulario)
            return self._generar_pregunta(primer_paso)
        
        return "❌ Error al iniciar el formulario."
    
    def procesar_respuesta(self, telefono: str, respuesta: str) -> Optional[str]:
        """Procesa la respuesta del usuario y devuelve la siguiente pregunta o resultado final"""
        estado = gestor_estados.obtener_estado(telefono)
        
        if not estado or not estado.get("tipo", "").startswith("formulario_"):
            return None
        
        datos = estado["datos"]
        paso_actual = datos["paso_actual"]
        
        # Validar respuesta actual
        if not self._validar_respuesta(paso_actual, respuesta, datos):
            return self._generar_pregunta(paso_actual, error=True)
        
        # Guardar respuesta
        campo_actual = self.pasos[paso_actual].campo
        respuesta_procesada = self._procesar_valor_respuesta(paso_actual, respuesta, datos)
        datos["respuestas"][campo_actual] = respuesta_procesada
        
        # Verificar si el formulario está completo
        siguiente_paso = self._obtener_siguiente_paso_valido(datos, paso_actual)
        
        if siguiente_paso is None:
            # Formulario completo, ejecutar callback
            resultado = self._ejecutar_callback(datos)
            gestor_estados.limpiar_estado(telefono)
            return resultado
        else:
            # Continuar al siguiente paso
            datos["paso_actual"] = siguiente_paso
            gestor_estados.establecer_estado(telefono, f"formulario_{self.tipo_formulario}", datos)
            return self._generar_pregunta(siguiente_paso)
    
    def _obtener_siguiente_paso_valido(self, datos: Dict, paso_actual: int) -> Optional[int]:
        """Encuentra el siguiente paso válido considerando dependencias"""
        for i in range(paso_actual + 1, len(self.pasos)):
            paso = self.pasos[i]
            
            # Verificar dependencia
            if paso.depende_de and paso.condicion_dependencia:
                valor_dependencia = datos["respuestas"].get(paso.depende_de)
                if not paso.condicion_dependencia(valor_dependencia):
                    continue
            
            return i
        
        return None
    
    def _generar_pregunta(self, paso_indice: int, error: bool = False) -> str:
        """Genera la pregunta para un paso específico"""
        paso = self.pasos[paso_indice]
        
        mensaje = ""
        if error:
            mensaje += "❌ Respuesta inválida. Por favor, intenta nuevamente.\n\n"
        
        mensaje += f"**{paso.pregunta}**"
        
        if paso.opciones:
            mensaje += f"\n\n📋 **Opciones disponibles:**"
            for i, opcion in enumerate(paso.opciones, 1):
                mensaje += f"\n{i}. {opcion}"
            mensaje += f"\n\n💡 Puedes responder con el número o escribir la opción."
        
        if not paso.obligatorio:
            mensaje += f"\n\n⚠️ *Campo opcional - envía 'saltar' para continuar*"
        
        # Mostrar progreso
        total_pasos = len([p for p in self.pasos if not p.depende_de or True])  # Simplificado
        mensaje += f"\n\n📊 Paso {paso_indice + 1} de {total_pasos}"
        
        return mensaje
    
    def _validar_respuesta(self, paso_indice: int, respuesta: str, datos: Dict) -> bool:
        """Valida la respuesta del usuario para el paso actual"""
        paso = self.pasos[paso_indice]
        respuesta = respuesta.strip()
        
        # Permitir saltar si no es obligatorio
        if not paso.obligatorio and respuesta.lower() in ['saltar', 'skip', 'omitir']:
            return True
        
        # Validar opciones predefinidas
        if paso.opciones:
            # Verificar si es un número válido
            if respuesta.isdigit():
                numero = int(respuesta)
                if 1 <= numero <= len(paso.opciones):
                    return True
            
            # Verificar si coincide con alguna opción (caso insensible)
            respuesta_lower = respuesta.lower()
            for opcion in paso.opciones:
                if respuesta_lower == opcion.lower() or respuesta_lower in opcion.lower():
                    return True
            
            return False
        
        # Validador personalizado
        if paso.validador:
            return paso.validador(respuesta, datos)
        
        # Por defecto, cualquier respuesta no vacía es válida
        return len(respuesta) > 0
    
    def _procesar_valor_respuesta(self, paso_indice: int, respuesta: str, datos: Dict) -> Any:
        """Procesa y convierte la respuesta al valor correcto"""
        paso = self.pasos[paso_indice]
        respuesta = respuesta.strip()
        
        # Saltar si no obligatorio
        if not paso.obligatorio and respuesta.lower() in ['saltar', 'skip', 'omitir']:
            return None
        
        # Procesar opciones predefinidas
        if paso.opciones:
            if respuesta.isdigit():
                numero = int(respuesta)
                if 1 <= numero <= len(paso.opciones):
                    return paso.opciones[numero - 1]
            
            # Buscar coincidencia por texto
            respuesta_lower = respuesta.lower()
            for opcion in paso.opciones:
                if respuesta_lower == opcion.lower() or respuesta_lower in opcion.lower():
                    return opcion
        
        return respuesta
    
    def _ejecutar_callback(self, datos: Dict) -> str:
        """Ejecuta la función callback cuando el formulario está completo"""
        try:
            callback_name = datos.get("callback")
            if callback_name == "completar_creacion_tarea":
                return completar_creacion_tarea(datos)
            else:
                return "❌ Error: Función de finalización no encontrada."
        except Exception as e:
            print(f"❌ Error ejecutando callback: {e}")
            return f"❌ Error al procesar el formulario: {str(e)}"


# ============ VALIDADORES ESPECÍFICOS ============

def validar_fecha(fecha_str: str, datos: Dict) -> bool:
    """Valida formato de fecha"""
    try:
        # Intentar varios formatos
        formatos = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m', '%d-%m']
        for formato in formatos:
            try:
                datetime.strptime(fecha_str, formato)
                return True
            except ValueError:
                continue
        
        # También permitir "hoy", "mañana", etc.
        palabras_validas = ['hoy', 'mañana', 'pasado mañana', 'la próxima semana']
        if fecha_str.lower() in palabras_validas:
            return True
        
        return False
    except:
        return False


def validar_usuario_empresa(usuario_str: str, datos: Dict) -> bool:
    """Valida que el usuario existe en la empresa"""
    try:
        # Obtener empresa_id de las respuestas anteriores
        empresa_id = datos["respuestas"].get("empresa_id")
        if not empresa_id:
            return True  # Se validará en el paso de empresa
        
        # Buscar usuario por nombre en la empresa
        response = supabase.table("usuarios_clientes") \
            .select("id, nombre") \
            .eq("empresa_id", empresa_id) \
            .ilike("nombre", f"%{usuario_str}%") \
            .execute()
        
        return len(response.data) > 0
    except:
        return True  # En caso de error, permitir continuar


def validar_empresa_acceso(empresa_str: str, datos: Dict) -> bool:
    """Valida que el usuario tiene acceso a la empresa"""
    try:
        usuario_datos = datos.get("usuario_datos", {})
        manager = PrivilegiosManager(usuario_datos)
        
        # Si es admin/superadmin, puede acceder a cualquier empresa
        if manager.get_tipo_usuario() in ["admin", "superadmin"]:
            return True
        
        # Si es cliente, validar sus empresas
        if usuario_datos.get("tipo") == "cliente":
            empresas_usuario = usuario_datos.get("empresas", [])
            empresa_lower = empresa_str.lower()
            
            for empresa in empresas_usuario:
                if empresa_lower in empresa.get("nombre_empresa", "").lower():
                    return True
        
        # Buscar empresa por nombre
        response = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .ilike("nombre_empresa", f"%{empresa_str}%") \
            .execute()
        
        return len(response.data) > 0
    except:
        return True


# ============ CALLBACKS DE FINALIZACIÓN ============

def completar_creacion_tarea(datos: Dict) -> str:
    """Completa la creación de una tarea con los datos recopilados"""
    try:
        respuestas = datos["respuestas"]
        usuario_datos = datos["usuario_datos"]
        
        # Procesar datos recopilados
        titulo = respuestas.get("titulo", "")
        descripcion = respuestas.get("descripcion", titulo)
        
        # Procesar empresa
        empresa_nombre = respuestas.get("empresa")
        empresa_response = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .ilike("nombre_empresa", f"%{empresa_nombre}%") \
            .limit(1) \
            .execute()
        
        if not empresa_response.data:
            return f"❌ Error: No se encontró la empresa '{empresa_nombre}'"
        
        empresa_id = empresa_response.data[0]["id"]
        empresa_nombre_real = empresa_response.data[0]["nombre_empresa"]
        
        # Procesar usuario asignado (opcional)
        usuario_asignado_id = None
        if respuestas.get("usuario_asignado"):
            usuario_nombre = respuestas["usuario_asignado"]
            if usuario_nombre.lower() not in ['ninguno', 'sin asignar', 'empresa']:
                usuario_response = supabase.table("usuarios_clientes") \
                    .select("id, nombre") \
                    .eq("empresa_id", empresa_id) \
                    .ilike("nombre", f"%{usuario_nombre}%") \
                    .limit(1) \
                    .execute()
                
                if usuario_response.data:
                    usuario_asignado_id = usuario_response.data[0]["id"]
        
        # Procesar fecha límite
        fecha_limite = None
        if respuestas.get("fecha_limite"):
            fecha_str = respuestas["fecha_limite"]
            fecha_limite = procesar_fecha_limite(fecha_str)
        
        # Procesar prioridad
        prioridad = respuestas.get("prioridad", "media").lower()
        if prioridad not in ["baja", "media", "alta", "crítica"]:
            prioridad = "media"
        
        # Crear tarea
        nueva_tarea = {
            "id": str(uuid.uuid4()),
            "titulo": titulo,
            "descripcion": descripcion,
            "empresa_id": empresa_id,
            "usuario_empresa_id": usuario_asignado_id,
            "prioridad": prioridad,
            "fecha_limite": fecha_limite,
            "estatus": "pendiente",
            "origen": "whatsapp",
            "activo": True,
            "asignada_a_empresa": usuario_asignado_id is None,
            "nombre_nora": usuario_datos.get("nombre_nora", "aura"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insertar en base de datos
        response = supabase.table("tareas").insert(nueva_tarea).execute()
        
        if response.data:
            tarea_creada = response.data[0]
            
            # Generar respuesta de confirmación
            mensaje_resultado = f"✅ **Tarea creada exitosamente**\n\n"
            mensaje_resultado += f"📋 **Título:** {titulo}\n"
            mensaje_resultado += f"🏢 **Empresa:** {empresa_nombre_real}\n"
            
            if usuario_asignado_id and usuario_response.data:
                mensaje_resultado += f"👤 **Asignado a:** {usuario_response.data[0]['nombre']}\n"
            else:
                mensaje_resultado += f"👥 **Asignado a:** Toda la empresa\n"
            
            mensaje_resultado += f"🎯 **Prioridad:** {prioridad.capitalize()}\n"
            
            if fecha_limite:
                mensaje_resultado += f"📅 **Fecha límite:** {fecha_limite}\n"
            
            mensaje_resultado += f"🆔 **ID:** {tarea_creada['id'][:8]}...\n"
            mensaje_resultado += f"\n💡 La tarea ya está disponible en el sistema."
            
            return mensaje_resultado
        else:
            return "❌ Error al crear la tarea en la base de datos."
            
    except Exception as e:
        print(f"❌ Error completando creación de tarea: {e}")
        return f"❌ Error al crear la tarea: {str(e)}"


def procesar_fecha_limite(fecha_str: str) -> Optional[str]:
    """Convierte texto de fecha a formato ISO"""
    try:
        fecha_str = fecha_str.lower().strip()
        hoy = datetime.now()
        
        if fecha_str in ['hoy']:
            return hoy.date().isoformat()
        elif fecha_str in ['mañana']:
            return (hoy + timedelta(days=1)).date().isoformat()
        elif fecha_str in ['pasado mañana']:
            return (hoy + timedelta(days=2)).date().isoformat()
        elif fecha_str in ['la próxima semana', 'próxima semana', 'siguiente semana']:
            return (hoy + timedelta(days=7)).date().isoformat()
        else:
            # Intentar parsear fecha específica
            formatos = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m', '%d-%m']
            for formato in formatos:
                try:
                    fecha_obj = datetime.strptime(fecha_str, formato)
                    # Si no tiene año, usar el año actual
                    if formato in ['%d/%m', '%d-%m']:
                        fecha_obj = fecha_obj.replace(year=hoy.year)
                    return fecha_obj.date().isoformat()
                except ValueError:
                    continue
        
        return None
    except:
        return None


# ============ FACTORY DE FORMULARIOS ============

def crear_formulario_tarea(usuario_datos: Dict) -> FormularioConversacional:
    """Crea el formulario conversacional para crear tareas"""
    
    manager = PrivilegiosManager(usuario_datos)
    empresas_disponibles = []
    
    # Determinar empresas disponibles según privilegios
    if manager.get_tipo_usuario() in ["admin", "superadmin"]:
        # Admin puede ver todas las empresas
        response = supabase.table("cliente_empresas") \
            .select("nombre_empresa") \
            .eq("activo", True) \
            .order("nombre_empresa") \
            .execute()
        empresas_disponibles = [emp["nombre_empresa"] for emp in response.data]
    elif usuario_datos.get("tipo") == "cliente":
        # Cliente solo ve sus empresas
        empresas_disponibles = [emp["nombre_empresa"] for emp in usuario_datos.get("empresas", [])]
    elif usuario_datos.get("tipo") == "usuario_cliente":
        # Empleado ve su empresa
        empresa_response = supabase.table("cliente_empresas") \
            .select("nombre_empresa") \
            .eq("id", usuario_datos.get("empresa_id")) \
            .execute()
        if empresa_response.data:
            empresas_disponibles = [empresa_response.data[0]["nombre_empresa"]]
    
    pasos = [
        PasoFormulario(
            campo="titulo",
            pregunta="¿Cuál es el título de la tarea?",
            obligatorio=True
        ),
        
        PasoFormulario(
            campo="descripcion", 
            pregunta="¿Puedes proporcionar una descripción detallada de la tarea?",
            obligatorio=False
        ),
        
        PasoFormulario(
            campo="empresa",
            pregunta="¿Para qué empresa es esta tarea?",
            opciones=empresas_disponibles if empresas_disponibles else None,
            validador=validar_empresa_acceso,
            obligatorio=True
        ),
        
        PasoFormulario(
            campo="usuario_asignado",
            pregunta="¿A quién quieres asignar esta tarea? (o escribe 'empresa' para asignar a toda la empresa)",
            validador=validar_usuario_empresa,
            obligatorio=False
        ),
        
        PasoFormulario(
            campo="prioridad",
            pregunta="¿Cuál es la prioridad de esta tarea?",
            opciones=["Baja", "Media", "Alta", "Crítica"],
            obligatorio=False
        ),
        
        PasoFormulario(
            campo="fecha_limite",
            pregunta="¿Cuál es la fecha límite? (ej: 'mañana', '15/12/2024', 'próxima semana')",
            validador=validar_fecha,
            obligatorio=False
        )
    ]
    
    return FormularioConversacional(
        tipo_formulario="tarea",
        pasos=pasos,
        callback_completar=completar_creacion_tarea,
        usuario_datos=usuario_datos
    )


# ============ FUNCIONES DE UTILIDAD ============

def obtener_formulario_activo(telefono: str) -> Optional[FormularioConversacional]:
    """Obtiene el formulario activo para un teléfono"""
    estado = gestor_estados.obtener_estado(telefono)
    
    if not estado or not estado.get("tipo", "").startswith("formulario_"):
        return None
    
    datos = estado["datos"]
    tipo_formulario = datos.get("tipo")
    
    if tipo_formulario == "tarea":
        return crear_formulario_tarea(datos.get("usuario_datos", {}))
    
    return None


def tiene_formulario_activo(telefono: str) -> bool:
    """Verifica si hay un formulario activo"""
    return obtener_formulario_activo(telefono) is not None


def cancelar_formulario(telefono: str) -> str:
    """Cancela el formulario activo"""
    gestor_estados.limpiar_estado(telefono)
    return "❌ Formulario cancelado. ¿En qué más puedo ayudarte?"
