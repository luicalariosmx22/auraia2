# 📁 clientes/aura/utils/menu_cliente.py

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime

def construir_menu_cliente(tipo_contacto, nombre_nora):
    """
    Construye un menú personalizado para clientes con acceso a información de su empresa
    """
    if tipo_contacto["tipo"] != "cliente":
        return "❌ Esta función solo está disponible para clientes registrados."
    
    cliente_id = tipo_contacto["id"]
    nombre_cliente = tipo_contacto["nombre"]
    empresas = tipo_contacto.get("empresas", [])
    
    if not empresas:
        return f"👋 Hola {nombre_cliente}! No tienes empresas asociadas en nuestro sistema."
    
    # Si tiene múltiples empresas, mostrar selector
    if len(empresas) > 1:
        menu = f"👋 Hola {nombre_cliente}! Tienes {len(empresas)} empresas registradas.\n\n"
        menu += "🏢 Selecciona una empresa para ver su información:\n\n"
        
        for i, empresa in enumerate(empresas, 1):
            nombre_empresa = empresa.get('nombre_empresa', 'Sin nombre')
            menu += f"{i}. {nombre_empresa}\n"
        
        menu += f"\n💬 Escribe el número de la empresa que te interesa."
        return menu
    
    # Si tiene una sola empresa, mostrar menú directo
    empresa = empresas[0]
    return construir_menu_empresa_especifica(empresa, nombre_cliente)

def construir_menu_empresa_especifica(empresa, nombre_cliente):
    """
    Construye el menú específico para una empresa
    """
    nombre_empresa = empresa.get('nombre_empresa', 'Su empresa')
    empresa_id = empresa.get('id')
    
    menu = f"👋 Hola {nombre_cliente}!\n\n"
    menu += f"🏢 Información disponible para {nombre_empresa}:\n\n"
    
    # Obtener estadísticas rápidas
    estadisticas = obtener_estadisticas_empresa(empresa_id)
    
    menu += "📋 **MENÚ DE OPCIONES:**\n\n"
    menu += "1️⃣ Ver tareas activas\n"
    menu += "2️⃣ Ver tareas completadas\n"
    menu += "3️⃣ Ver brief de la empresa\n"
    menu += "4️⃣ Próximas reuniones\n"
    menu += "5️⃣ Estadísticas del proyecto\n"
    menu += "6️⃣ Contactar con el equipo\n\n"
    
    # Agregar estadísticas rápidas
    if estadisticas:
        menu += f"📊 **RESUMEN RÁPIDO:**\n"
        menu += f"✅ Tareas completadas: {estadisticas.get('completadas', 0)}\n"
        menu += f"⏳ Tareas activas: {estadisticas.get('activas', 0)}\n"
        menu += f"📅 Última actividad: {estadisticas.get('ultima_actividad', 'N/A')}\n\n"
    
    menu += "💬 Escribe el número de la opción que te interesa."
    
    return menu

def obtener_estadisticas_empresa(empresa_id):
    """
    Obtiene estadísticas rápidas de una empresa
    """
    try:
        # Buscar tareas activas
        tareas_activas = supabase.table("tareas") \
            .select("id") \
            .eq("empresa_id", empresa_id) \
            .eq("estatus", "activa") \
            .execute()
        
        # Buscar tareas completadas
        tareas_completadas = supabase.table("tareas") \
            .select("id") \
            .eq("empresa_id", empresa_id) \
            .eq("estatus", "completada") \
            .execute()
        
        # Buscar última actividad
        ultima_actividad = supabase.table("tareas") \
            .select("fecha_actualizacion") \
            .eq("empresa_id", empresa_id) \
            .order("fecha_actualizacion", desc=True) \
            .limit(1) \
            .execute()
        
        fecha_ultima = "N/A"
        if ultima_actividad.data:
            fecha_str = ultima_actividad.data[0].get("fecha_actualizacion")
            if fecha_str:
                try:
                    fecha_obj = datetime.fromisoformat(fecha_str.replace('Z', ''))
                    fecha_ultima = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_ultima = "N/A"
        
        return {
            "activas": len(tareas_activas.data) if tareas_activas.data else 0,
            "completadas": len(tareas_completadas.data) if tareas_completadas.data else 0,
            "ultima_actividad": fecha_ultima
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return {}

def procesar_seleccion_menu_cliente(seleccion, tipo_contacto, nombre_nora):
    """
    Procesa la selección del menú del cliente
    """
    if tipo_contacto["tipo"] != "cliente":
        return "❌ Esta función solo está disponible para clientes registrados."
    
    empresas = tipo_contacto.get("empresas", [])
    if not empresas:
        return "❌ No tienes empresas asociadas."
    
    # Si hay múltiples empresas y la selección es un número para elegir empresa
    if len(empresas) > 1 and seleccion.isdigit():
        indice = int(seleccion) - 1
        if 0 <= indice < len(empresas):
            empresa_seleccionada = empresas[indice]
            return construir_menu_empresa_especifica(empresa_seleccionada, tipo_contacto["nombre"])
        else:
            return "❌ Número de empresa inválido. Por favor, elige un número válido."
    
    # Procesar selección de opción del menú
    empresa = empresas[0] if len(empresas) == 1 else None
    if not empresa:
        return "❌ Error: No se pudo identificar la empresa."
    
    return procesar_opcion_empresa(seleccion, empresa, tipo_contacto["nombre"])

def procesar_opcion_empresa(seleccion, empresa, nombre_cliente):
    """
    Procesa las opciones específicas de la empresa
    """
    empresa_id = empresa.get('id')
    nombre_empresa = empresa.get('nombre_empresa', 'Su empresa')
    
    if seleccion == "1":
        return obtener_tareas_activas(empresa_id, nombre_empresa)
    elif seleccion == "2":
        return obtener_tareas_completadas(empresa_id, nombre_empresa)
    elif seleccion == "3":
        return obtener_brief_empresa(empresa, nombre_empresa)
    elif seleccion == "4":
        return obtener_proximas_reuniones(empresa_id, nombre_empresa)
    elif seleccion == "5":
        return obtener_estadisticas_detalladas(empresa_id, nombre_empresa)
    elif seleccion == "6":
        return obtener_contacto_equipo(nombre_empresa)
    else:
        return f"❌ Opción inválida. Por favor, elige un número del 1 al 6.\n\nEscribe 'menu' para ver las opciones disponibles para {nombre_empresa}."

def obtener_tareas_activas(empresa_id, nombre_empresa):
    """
    Obtiene las tareas activas de una empresa
    """
    try:
        tareas = supabase.table("tareas") \
            .select("titulo, descripcion, fecha_limite, prioridad") \
            .eq("empresa_id", empresa_id) \
            .eq("estatus", "activa") \
            .order("fecha_limite", desc=False) \
            .limit(10) \
            .execute()
        
        if not tareas.data:
            return f"✅ {nombre_empresa} no tiene tareas activas en este momento."
        
        respuesta = f"⏳ **TAREAS ACTIVAS - {nombre_empresa}**\n\n"
        
        for i, tarea in enumerate(tareas.data, 1):
            titulo = tarea.get('titulo', 'Sin título')
            descripcion = tarea.get('descripcion', 'Sin descripción')
            fecha_limite = tarea.get('fecha_limite', 'Sin fecha')
            prioridad = tarea.get('prioridad', 'Normal')
            
            # Formatear fecha
            if fecha_limite and fecha_limite != 'Sin fecha':
                try:
                    fecha_obj = datetime.fromisoformat(fecha_limite.replace('Z', ''))
                    fecha_formato = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_formato = fecha_limite
            else:
                fecha_formato = "Sin fecha límite"
            
            # Emoji por prioridad
            emoji_prioridad = "🔴" if prioridad == "Alta" else "🟡" if prioridad == "Media" else "🟢"
            
            respuesta += f"{i}. {emoji_prioridad} **{titulo}**\n"
            respuesta += f"   📝 {descripcion[:100]}{'...' if len(descripcion) > 100 else ''}\n"
            respuesta += f"   📅 Fecha límite: {fecha_formato}\n\n"
        
        respuesta += f"💬 ¿Necesitas más detalles sobre alguna tarea específica?"
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error obteniendo tareas activas: {e}")
        return f"❌ Error al obtener las tareas activas de {nombre_empresa}."

def obtener_tareas_completadas(empresa_id, nombre_empresa):
    """
    Obtiene las tareas completadas de una empresa
    """
    try:
        tareas = supabase.table("tareas") \
            .select("titulo, descripcion, fecha_completado") \
            .eq("empresa_id", empresa_id) \
            .eq("estatus", "completada") \
            .order("fecha_completado", desc=True) \
            .limit(10) \
            .execute()
        
        if not tareas.data:
            return f"📝 {nombre_empresa} aún no tiene tareas completadas."
        
        respuesta = f"✅ **TAREAS COMPLETADAS - {nombre_empresa}**\n\n"
        
        for i, tarea in enumerate(tareas.data, 1):
            titulo = tarea.get('titulo', 'Sin título')
            fecha_completado = tarea.get('fecha_completado', 'Sin fecha')
            
            # Formatear fecha
            if fecha_completado and fecha_completado != 'Sin fecha':
                try:
                    fecha_obj = datetime.fromisoformat(fecha_completado.replace('Z', ''))
                    fecha_formato = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_formato = fecha_completado
            else:
                fecha_formato = "Fecha no registrada"
            
            respuesta += f"{i}. ✅ **{titulo}**\n"
            respuesta += f"   📅 Completada: {fecha_formato}\n\n"
        
        respuesta += f"🎉 ¡Excelente progreso en {nombre_empresa}!"
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error obteniendo tareas completadas: {e}")
        return f"❌ Error al obtener las tareas completadas de {nombre_empresa}."

def obtener_brief_empresa(empresa, nombre_empresa):
    """
    Obtiene el brief de la empresa
    """
    brief = empresa.get('brief', '').strip()
    
    if not brief:
        return f"📝 **BRIEF - {nombre_empresa}**\n\nNo hay brief registrado para esta empresa."
    
    respuesta = f"📝 **BRIEF - {nombre_empresa}**\n\n"
    respuesta += brief
    respuesta += f"\n\n💬 ¿Necesitas alguna aclaración sobre el brief?"
    
    return respuesta

def obtener_proximas_reuniones(empresa_id, nombre_empresa):
    """
    Obtiene las próximas reuniones de una empresa
    """
    try:
        # Buscar reuniones futuras
        reuniones = supabase.table("reuniones") \
            .select("titulo, fecha_reunion, descripcion, tipo") \
            .eq("empresa_id", empresa_id) \
            .gte("fecha_reunion", datetime.now().isoformat()) \
            .order("fecha_reunion", desc=False) \
            .limit(5) \
            .execute()
        
        if not reuniones.data:
            return f"📅 **PRÓXIMAS REUNIONES - {nombre_empresa}**\n\nNo hay reuniones programadas próximamente."
        
        respuesta = f"📅 **PRÓXIMAS REUNIONES - {nombre_empresa}**\n\n"
        
        for i, reunion in enumerate(reuniones.data, 1):
            titulo = reunion.get('titulo', 'Reunión sin título')
            fecha = reunion.get('fecha_reunion', 'Sin fecha')
            descripcion = reunion.get('descripcion', 'Sin descripción')
            tipo = reunion.get('tipo', 'General')
            
            # Formatear fecha
            if fecha and fecha != 'Sin fecha':
                try:
                    fecha_obj = datetime.fromisoformat(fecha.replace('Z', ''))
                    fecha_formato = fecha_obj.strftime("%d/%m/%Y %H:%M")
                except:
                    fecha_formato = fecha
            else:
                fecha_formato = "Fecha por confirmar"
            
            respuesta += f"{i}. 📅 **{titulo}**\n"
            respuesta += f"   🕒 {fecha_formato}\n"
            respuesta += f"   📋 Tipo: {tipo}\n"
            if descripcion and descripcion != 'Sin descripción':
                respuesta += f"   📝 {descripcion[:100]}{'...' if len(descripcion) > 100 else ''}\n"
            respuesta += "\n"
        
        respuesta += f"💬 ¿Necesitas más información sobre alguna reunión?"
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error obteniendo reuniones: {e}")
        return f"❌ Error al obtener las reuniones de {nombre_empresa}."

def obtener_estadisticas_detalladas(empresa_id, nombre_empresa):
    """
    Obtiene estadísticas detalladas de una empresa
    """
    try:
        # Estadísticas de tareas
        estadisticas = obtener_estadisticas_empresa(empresa_id)
        
        # Obtener más detalles
        tareas_por_prioridad = supabase.table("tareas") \
            .select("prioridad") \
            .eq("empresa_id", empresa_id) \
            .eq("estatus", "activa") \
            .execute()
        
        alta = media = baja = 0
        if tareas_por_prioridad.data:
            for tarea in tareas_por_prioridad.data:
                prioridad = tarea.get('prioridad', 'Baja')
                if prioridad == 'Alta':
                    alta += 1
                elif prioridad == 'Media':
                    media += 1
                else:
                    baja += 1
        
        respuesta = f"📊 **ESTADÍSTICAS - {nombre_empresa}**\n\n"
        respuesta += f"✅ Tareas completadas: {estadisticas.get('completadas', 0)}\n"
        respuesta += f"⏳ Tareas activas: {estadisticas.get('activas', 0)}\n\n"
        
        if estadisticas.get('activas', 0) > 0:
            respuesta += f"**Distribución por prioridad:**\n"
            respuesta += f"🔴 Alta prioridad: {alta}\n"
            respuesta += f"🟡 Media prioridad: {media}\n"
            respuesta += f"🟢 Baja prioridad: {baja}\n\n"
        
        respuesta += f"📅 Última actividad: {estadisticas.get('ultima_actividad', 'N/A')}\n\n"
        respuesta += f"📈 El proyecto avanza según lo planificado."
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return f"❌ Error al obtener las estadísticas de {nombre_empresa}."

def obtener_contacto_equipo(nombre_empresa):
    """
    Proporciona información de contacto del equipo
    """
    respuesta = f"👥 **CONTACTO CON EL EQUIPO - {nombre_empresa}**\n\n"
    respuesta += f"Para contactar directamente con tu equipo asignado:\n\n"
    respuesta += f"📧 Email: equipo@agenciaaura.mx\n"
    respuesta += f"📱 WhatsApp: Este mismo número\n"
    respuesta += f"🌐 Portal: www.agenciaaura.mx\n\n"
    respuesta += f"💬 También puedes escribir aquí cualquier pregunta o solicitud específica sobre {nombre_empresa}."
    
    return respuesta
