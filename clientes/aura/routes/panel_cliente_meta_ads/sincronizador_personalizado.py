# clientes/aura/routes/panel_cliente_meta_ads/sincronizador_personalizado.py
# Este archivo maneja sincronizaciones personalizadas para casos específicos

from datetime import datetime, timedelta
import uuid
from clientes.aura.utils.supabase_client import supabase

def obtener_rango_semana_actual():
    """Obtiene el rango de fechas de la semana actual para reportes"""
    hoy = datetime.utcnow().date()
    fin = hoy - timedelta(days=hoy.weekday() + 1)
    inicio = fin - timedelta(days=6)
    
    # Para datos de Meta Ads, usar el rango exacto que está en la base
    # Los datos actuales van de 2025-07-28 a 2025-08-04
    inicio = datetime(2025, 7, 28).date()
    fin = datetime(2025, 8, 4).date()
    
    return inicio.isoformat(), fin.isoformat()

def sincronizar_cuentas_especificas(cuentas_ids, motivo="sincronización personalizada", fecha_inicio_custom=None, fecha_fin_custom=None):
    """
    Sincroniza reportes semanales para cuentas específicas.
    
    Args:
        cuentas_ids: Lista de IDs de cuentas publicitarias a procesar
        motivo: Descripción del motivo de la sincronización (para logs)
        fecha_inicio_custom: Fecha de inicio personalizada (formato YYYY-MM-DD)
        fecha_fin_custom: Fecha de fin personalizada (formato YYYY-MM-DD)
    
    Returns:
        int: Número de reportes insertados
    """
    if not cuentas_ids:
        print("❌ No se proporcionaron cuentas para sincronizar")
        return 0
        
    # Usar fechas personalizadas o el rango semanal por defecto
    if fecha_inicio_custom and fecha_fin_custom:
        fecha_inicio, fecha_fin = fecha_inicio_custom, fecha_fin_custom
        print(f"📅 Usando rango personalizado: {fecha_inicio} al {fecha_fin}")
    else:
        fecha_inicio, fecha_fin = obtener_rango_semana_actual()
        print(f"📆 Usando rango semanal: {fecha_inicio} al {fecha_fin}")
        
    print(f"🎯 {motivo.capitalize()}: Procesando {len(cuentas_ids)} cuentas específicas: {cuentas_ids}")

    # Obtener datos de anuncios para el rango de fechas (exactamente igual que sincronizador_semanal.py)
    query = supabase.table("meta_ads_anuncios_detalle").select("*").gte("fecha_inicio", fecha_inicio).lte("fecha_fin", fecha_fin)
    
    # Si tenemos cuentas específicas, filtrar por ellas
    if cuentas_ids:
        query = query.in_("id_cuenta_publicitaria", cuentas_ids)
    
    anuncios_res = query.execute()
    anuncios = anuncios_res.data
    
    print(f"📊 Encontrados {len(anuncios) if anuncios else 0} registros de anuncios")
    
    # Debug: mostrar la consulta exacta que se está ejecutando
    print(f"🔍 DEBUG - Consulta ejecutada:")
    print(f"   - Tabla: meta_ads_anuncios_detalle")
    print(f"   - Filtros: fecha_inicio >= '{fecha_inicio}' AND fecha_fin <= '{fecha_fin}'")
    print(f"   - Cuentas: {cuentas_ids}")
    
    if not anuncios:
        # Verificar si existen datos para esas cuentas sin filtro de fechas
        print("🔍 Verificando si existen datos sin filtro de fechas...")
        test_query = supabase.table("meta_ads_anuncios_detalle").select("fecha_inicio, fecha_fin, id_cuenta_publicitaria").in_("id_cuenta_publicitaria", cuentas_ids).limit(5)
        test_result = test_query.execute()
        
        if test_result.data:
            print(f"✅ Sí existen {len(test_result.data)} registros para estas cuentas:")
            for registro in test_result.data:
                print(f"   - Cuenta: {registro.get('id_cuenta_publicitaria')}, Fecha inicio: {registro.get('fecha_inicio')}, Fecha fin: {registro.get('fecha_fin')}")
            print(f"⚠️ El problema es el rango de fechas: {fecha_inicio} - {fecha_fin}")
        else:
            print("❌ No existen datos para estas cuentas en absoluto")
            
        print("⚠️ No hay datos de anuncios para estas cuentas en este rango de fechas.")
        return 0

    # Obtener información de las cuentas
    print("🔄 Obteniendo información de cuentas...")
    cuentas_info_result = supabase.table("meta_ads_cuentas")\
        .select("id_cuenta_publicitaria, empresa_id, estado_actual, nombre_cliente")\
        .in_("id_cuenta_publicitaria", cuentas_ids)\
        .execute()
    
    # Crear un mapa para lookup rápido
    cuentas_map = {}
    for cuenta_info in cuentas_info_result.data:
        cuenta_id = cuenta_info["id_cuenta_publicitaria"]
        cuentas_map[cuenta_id] = cuenta_info
    
    print(f"📋 Información obtenida para {len(cuentas_map)} cuentas")

    # Agrupar por empresa_id y cuenta (permitir cuentas sin empresa_id)
    agrupados = {}
    cuentas_sin_info = set()
    cuentas_excluidas = set()
    cuentas_sin_empresa = set()
    
    for a in anuncios:
        cuenta_id = a.get("id_cuenta_publicitaria")
        
        # Lookup rápido en el mapa
        cuenta_info = cuentas_map.get(cuenta_id)
        if not cuenta_info:
            cuentas_sin_info.add(cuenta_id)
            continue
            
        empresa_id = cuenta_info.get("empresa_id")
        estado_actual = cuenta_info.get("estado_actual")
        
        # Excluir cuentas con estado 'excluida'
        if estado_actual == 'excluida':
            cuentas_excluidas.add(cuenta_id)
            continue
            
        # Procesar cuentas tanto con empresa_id como sin empresa_id
        if not empresa_id:
            cuentas_sin_empresa.add(cuenta_id)
            # Para cuentas sin empresa, usar None como empresa_id
            clave = (None, cuenta_id)
        else:
            clave = (empresa_id, cuenta_id)
            
        if clave not in agrupados:
            agrupados[clave] = []
        agrupados[clave].append(a)
    
    # Logging detallado
    if cuentas_sin_info:
        print(f"⚠️ Cuentas sin información en meta_ads_cuentas ({len(cuentas_sin_info)}): {list(cuentas_sin_info)}")
    
    if cuentas_excluidas:
        print(f"🚫 Cuentas excluidas del reporte ({len(cuentas_excluidas)}): {list(cuentas_excluidas)}")
    
    if cuentas_sin_empresa:
        print(f"ℹ️ Cuentas sin empresa_id asignado (se procesarán igual) ({len(cuentas_sin_empresa)}): {list(cuentas_sin_empresa)}")
    
    print(f"📊 Procesando {len(agrupados)} combinaciones empresa-cuenta")

    # Insertar reportes por cuenta
    registros = []
    for (empresa_id, cuenta_id), items in agrupados.items():
        # Separar datos por plataforma
        facebook_items = [x for x in items if x.get("publisher_platform") == "facebook"]
        instagram_items = [x for x in items if x.get("publisher_platform") == "instagram"]
        
        # Obtener nombre de empresa
        empresa_nombre = None
        if empresa_id:
            try:
                empresa_res = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", empresa_id).single().execute()
                empresa_nombre = empresa_res.data.get("nombre_empresa") if empresa_res.data else None
            except:
                pass
        
        reporte = {
            "id": str(uuid.uuid4()),
            "empresa_id": empresa_id,
            "id_cuenta_publicitaria": cuenta_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_campañas": len(set([x["campana_id"] for x in items if x.get("campana_id")])),
            "importe_gastado_campañas": sum([float(x.get("importe_gastado", 0) or 0) for x in items]),
            "total_conjuntos": len(set([x["conjunto_id"] for x in items if x.get("conjunto_id")])),
            "importe_gastado_conjuntos": sum([float(x.get("importe_gastado", 0) or 0) for x in items]),
            "total_anuncios": len(set([x["ad_id"] for x in items if x.get("ad_id")])),
            "importe_gastado_anuncios": sum([float(x.get("importe_gastado", 0) or 0) for x in items]),
            "impresiones": sum([int(x.get("impresiones", 0) or 0) for x in items]),
            "alcance": sum([int(x.get("alcance", 0) or 0) for x in items]),
            "clicks": sum([int(x.get("clicks", 0) or 0) for x in items]),
            "link_clicks": sum([int(x.get("link_clicks", 0) or 0) for x in items]),
            "mensajes": sum([int(x.get("messaging_conversations_started", 0) or 0) for x in items]),
            "interacciones": sum([int(x.get("interacciones", 0) or 0) for x in items]),
            "video_plays": sum([int(x.get("video_plays", 0) or 0) for x in items]),
            "reproducciones_video_3s": sum([int(x.get("reproducciones_video_3s", 0) or 0) for x in items]),
            # Facebook específico
            "facebook_impresiones": sum([int(x.get("impresiones", 0) or 0) for x in facebook_items]),
            "facebook_alcance": sum([int(x.get("alcance", 0) or 0) for x in facebook_items]),
            "facebook_clicks": sum([int(x.get("clicks", 0) or 0) for x in facebook_items]),
            "facebook_mensajes": sum([int(x.get("messaging_conversations_started", 0) or 0) for x in facebook_items]),
            "facebook_importe_gastado": sum([float(x.get("importe_gastado", 0) or 0) for x in facebook_items]),
            # Instagram específico
            "instagram_impresiones": sum([int(x.get("impresiones", 0) or 0) for x in instagram_items]),
            "instagram_alcance": sum([int(x.get("alcance", 0) or 0) for x in instagram_items]),
            "instagram_clicks": sum([int(x.get("clicks", 0) or 0) for x in instagram_items]),
            "instagram_mensajes": sum([int(x.get("messaging_conversations_started", 0) or 0) for x in instagram_items]),
            "instagram_importe_gastado": sum([float(x.get("importe_gastado", 0) or 0) for x in instagram_items]),
            # Metadatos
            "empresa_nombre": empresa_nombre,
            "public_token": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
        }

        # Verificar si ya existe (permitir actualización)
        existente = supabase.table("meta_ads_reportes_semanales") \
            .select("id") \
            .eq("empresa_id", empresa_id) \
            .eq("id_cuenta_publicitaria", cuenta_id) \
            .eq("fecha_inicio", fecha_inicio) \
            .eq("fecha_fin", fecha_fin) \
            .execute()

        if not existente.data:
            registros.append(reporte)
            print(f"✅ Nuevo reporte para cuenta {cuenta_id} ({cuentas_map.get(cuenta_id, {}).get('nombre_cliente', 'Sin nombre')})")
        else:
            print(f"ℹ️ Reporte ya existe para cuenta {cuenta_id}, se omite")

    # Insertar reportes
    if registros:
        supabase.table("meta_ads_reportes_semanales").insert(registros).execute()
        print(f"✅ Se insertaron {len(registros)} reportes nuevos para {motivo}")
        return len(registros)
    else:
        print("ℹ️ No se insertaron reportes nuevos. Todas las cuentas ya tienen reportes para esta semana.")
        return 0

def sincronizar_cuentas_nuevas(nombre_nora):
    """
    Sincroniza solo las cuentas que no tienen reportes previos para un cliente.
    
    Args:
        nombre_nora: Nombre del cliente
    
    Returns:
        int: Número de reportes insertados
    """
    print(f"🔍 Buscando cuentas nuevas (sin reportes) para '{nombre_nora}'...")
    
    try:
        # Obtener empresa_id
        empresa_resultado = supabase.table('cliente_empresas')\
            .select('id')\
            .eq('nombre_nora', nombre_nora)\
            .execute()
        
        if not empresa_resultado.data:
            print(f"❌ No se encontró empresa para '{nombre_nora}'")
            return 0
            
        empresa_id = empresa_resultado.data[0]['id']
        
        # Obtener todas las cuentas activas de la empresa
        cuentas_result = supabase.table("meta_ads_cuentas")\
            .select("id_cuenta_publicitaria, nombre_cliente")\
            .eq("empresa_id", empresa_id)\
            .neq("estado_actual", "excluida")\
            .execute()
            
        if not cuentas_result.data:
            print(f"⚠️ No se encontraron cuentas activas para '{nombre_nora}'")
            return 0
            
        todas_las_cuentas = [cuenta["id_cuenta_publicitaria"] for cuenta in cuentas_result.data]
        print(f"📋 Encontradas {len(todas_las_cuentas)} cuentas activas total")
        
        # Obtener cuentas que ya tienen reportes
        fecha_inicio, fecha_fin = obtener_rango_semana_actual()
        reportes_existentes = supabase.table("meta_ads_reportes_semanales")\
            .select("id_cuenta_publicitaria")\
            .eq("empresa_id", empresa_id)\
            .eq("fecha_inicio", fecha_inicio)\
            .eq("fecha_fin", fecha_fin)\
            .execute()
            
        cuentas_con_reportes = set([r["id_cuenta_publicitaria"] for r in reportes_existentes.data])
        print(f"📊 Cuentas que ya tienen reportes: {len(cuentas_con_reportes)}")
        
        # Encontrar cuentas nuevas (sin reportes)
        cuentas_nuevas = [cuenta for cuenta in todas_las_cuentas if cuenta not in cuentas_con_reportes]
        
        if not cuentas_nuevas:
            print("ℹ️ No hay cuentas nuevas para sincronizar. Todas las cuentas ya tienen reportes.")
            return 0
            
        print(f"🆕 Encontradas {len(cuentas_nuevas)} cuentas nuevas sin reportes: {cuentas_nuevas}")
        
        # Sincronizar solo las cuentas nuevas
        return sincronizar_cuentas_especificas(
            cuentas_nuevas, 
            f"sincronización de cuentas nuevas para {nombre_nora}"
        )
        
    except Exception as e:
        print(f"❌ Error buscando cuentas nuevas para {nombre_nora}: {e}")
        return 0

def sincronizar_cuentas_recien_importadas(empresa_id, minutos_recientes=60):
    """
    Sincroniza cuentas que fueron importadas recientemente.
    
    Args:
        empresa_id: ID de la empresa
        minutos_recientes: Considerar cuentas importadas en los últimos X minutos (default: 60)
    
    Returns:
        int: Número de reportes insertados
    """
    tiempo_limite = datetime.utcnow() - timedelta(minutes=minutos_recientes)
    
    print(f"🔍 Buscando cuentas importadas en los últimos {minutos_recientes} minutos...")
    
    try:
        # Buscar cuentas importadas recientemente
        cuentas_recientes = supabase.table("meta_ads_cuentas")\
            .select("id_cuenta_publicitaria, nombre_cliente, created_at")\
            .eq("empresa_id", empresa_id)\
            .neq("estado_actual", "excluida")\
            .gte("created_at", tiempo_limite.isoformat())\
            .execute()
            
        if not cuentas_recientes.data:
            print("ℹ️ No se encontraron cuentas importadas recientemente")
            return 0
            
        cuentas_ids = [cuenta["id_cuenta_publicitaria"] for cuenta in cuentas_recientes.data]
        print(f"🆕 Encontradas {len(cuentas_ids)} cuentas recién importadas:")
        
        for cuenta in cuentas_recientes.data:
            print(f"   - {cuenta['id_cuenta_publicitaria']} ({cuenta.get('nombre_cliente', 'Sin nombre')})")
        
        # Sincronizar las cuentas recién importadas
        return sincronizar_cuentas_especificas(
            cuentas_ids, 
            "sincronización de cuentas recién importadas"
        )
        
    except Exception as e:
        print(f"❌ Error buscando cuentas recién importadas: {e}")
        return 0

if __name__ == "__main__":
    # Ejemplos de uso:
    
    # Sincronizar cuentas específicas
    # sincronizar_cuentas_especificas(["123456789", "987654321"])
    
    # Sincronizar solo cuentas nuevas para un cliente
    # sincronizar_cuentas_nuevas("cliente_ejemplo")
    
    # Sincronizar cuentas recién importadas (últimos 60 minutos)
    # sincronizar_cuentas_recien_importadas("empresa_id_ejemplo", 60)
    
    print("📋 Funciones disponibles:")
    print("   - sincronizar_cuentas_especificas(cuentas_ids, motivo)")
    print("   - sincronizar_cuentas_nuevas(nombre_nora)")
    print("   - sincronizar_cuentas_recien_importadas(empresa_id, minutos)")
