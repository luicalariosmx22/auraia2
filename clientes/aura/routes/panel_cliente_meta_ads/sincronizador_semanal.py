# clientes/aura/routes/panel_cliente_meta_ads/sincronizador_semanal.py
#Este es el archivo que hace los reportes y los sube en meta_ads_reportes_semanales

from datetime import datetime, timedelta
import uuid
from clientes.aura.utils.supabase_client import supabase

def obtener_rango_semana_actual():
    hoy = datetime.utcnow().date()
    fin = hoy - timedelta(days=hoy.weekday() + 1)
    inicio = fin - timedelta(days=6)
    
    # Para datos de Meta Ads, usar el rango exacto que está en la base
    # Los datos actuales van de 2025-07-28 a 2025-08-04
    inicio = datetime(2025, 7, 28).date()
    fin = datetime(2025, 8, 4).date()
    
    return inicio.isoformat(), fin.isoformat()

def sincronizar_reportes_semanales(nombre_nora=None):
    fecha_inicio, fecha_fin = obtener_rango_semana_actual()
    print(f"📆 Sincronizando semana del {fecha_inicio} al {fecha_fin}")

    # Obtener cuentas publicitarias para el nombre_nora si se proporciona
    cuentas_ids = None
    empresa_id_cliente = None
    if nombre_nora:
        try:
            # Obtener empresa_id primero
            empresa_resultado = supabase.table('cliente_empresas')\
                .select('id')\
                .eq('nombre_nora', nombre_nora)\
                .execute()
            
            if empresa_resultado.data:
                empresa_id_cliente = empresa_resultado.data[0]['id']
                
                # Obtener cuentas de Meta Ads de la empresa
                cuentas_result = supabase.table("meta_ads_cuentas")\
                    .select("id_cuenta_publicitaria")\
                    .eq("empresa_id", empresa_id_cliente)\
                    .neq("estado_actual", "excluida")\
                    .execute()
                    
                if cuentas_result.data:
                    cuentas_ids = [cuenta["id_cuenta_publicitaria"] for cuenta in cuentas_result.data]
                    print(f"🔍 Encontradas {len(cuentas_ids)} cuentas activas para '{nombre_nora}': {cuentas_ids}")
                else:
                    print(f"⚠️ No se encontraron cuentas activas para '{nombre_nora}'. Procesando todas las cuentas no excluidas.")
                    # No retornamos 0 aquí, permitimos procesar todas las cuentas
            else:
                print(f"⚠️ No se encontró empresa para '{nombre_nora}'")
                return 0
                
        except Exception as e:
            print(f"❌ Error obteniendo cuentas para {nombre_nora}: {e}")
            return 0

    # Obtener datos de anuncios para el rango de fechas
    query = supabase.table("meta_ads_anuncios_detalle").select("*").gte("fecha_inicio", fecha_inicio).lte("fecha_fin", fecha_fin)
    
    # Si tenemos cuentas específicas, filtrar por ellas
    if cuentas_ids:
        query = query.in_("id_cuenta_publicitaria", cuentas_ids)
    
    anuncios_res = query.execute()
    anuncios = anuncios_res.data
    
    print(f"📊 Encontrados {len(anuncios) if anuncios else 0} registros de anuncios")
    
    if not anuncios:
        print("⚠️ No hay datos de anuncios para esta semana.")
        return 0

    # OPTIMIZACIÓN: Obtener todas las cuentas de una vez
    print("🔄 Obteniendo información de cuentas...")
    cuentas_unicas = list(set([a.get("id_cuenta_publicitaria") for a in anuncios if a.get("id_cuenta_publicitaria")]))
    
    # Una sola query para todas las cuentas
    cuentas_info_result = supabase.table("meta_ads_cuentas")\
        .select("id_cuenta_publicitaria, empresa_id, estado_actual")\
        .in_("id_cuenta_publicitaria", cuentas_unicas)\
        .execute()
    
    # Crear un mapa para lookup rápido
    cuentas_map = {}
    for cuenta_info in cuentas_info_result.data:
        cuenta_id = cuenta_info["id_cuenta_publicitaria"]
        cuentas_map[cuenta_id] = cuenta_info
    
    print(f"📋 Información obtenida para {len(cuentas_map)} cuentas")

    # Agrupar por empresa_id y cuenta (ahora más rápido)
    agrupados = {}
    cuentas_sin_info = set()
    cuentas_excluidas = set()
    cuentas_sin_empresa = set()
    
    for a in anuncios:
        cuenta_id = a.get("id_cuenta_publicitaria")
        
        # Lookup rápido en el mapa (sin query)
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
            
        if not empresa_id:
            cuentas_sin_empresa.add(cuenta_id)
            continue
            
        if empresa_id:
            clave = (empresa_id, cuenta_id)
            if clave not in agrupados:
                agrupados[clave] = []
            agrupados[clave].append(a)
    
    # Logging detallado de cuentas sin reportes
    if cuentas_sin_info:
        print(f"⚠️ Cuentas sin información en meta_ads_cuentas ({len(cuentas_sin_info)}): {list(cuentas_sin_info)}")
    
    if cuentas_excluidas:
        print(f"🚫 Cuentas excluidas del reporte ({len(cuentas_excluidas)}): {list(cuentas_excluidas)}")
    
    if cuentas_sin_empresa:
        print(f"❓ Cuentas sin empresa_id asignado ({len(cuentas_sin_empresa)}): {list(cuentas_sin_empresa)}")
    
    print(f"📊 Agrupados en {len(agrupados)} combinaciones empresa-cuenta")

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
            "id_cuenta_publicitaria": cuenta_id,  # Campo correcto
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
            "nombre_nora": nombre_nora,
            "public_token": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
        }

        # Verifica si ya existe
        existente = supabase.table("meta_ads_reportes_semanales") \
            .select("id") \
            .eq("empresa_id", empresa_id) \
            .eq("id_cuenta_publicitaria", cuenta_id) \
            .eq("fecha_inicio", fecha_inicio) \
            .eq("fecha_fin", fecha_fin) \
            .execute()

        if not existente.data:
            registros.append(reporte)
        else:
            print(f"ℹ️ Reporte ya existe para empresa {empresa_id}, cuenta {cuenta_id}")

    # Resumen final detallado
    total_cuentas_con_datos = len(set([a.get("id_cuenta_publicitaria") for a in anuncios]))
    cuentas_procesadas = len(agrupados)
    cuentas_sin_procesar = total_cuentas_con_datos - cuentas_procesadas
    
    print(f"\n📊 RESUMEN DE PROCESAMIENTO:")
    print(f"   📈 Total de anuncios encontrados: {len(anuncios)}")
    print(f"   🏢 Total de cuentas con datos: {total_cuentas_con_datos}")
    print(f"   ✅ Cuentas procesadas para reportes: {cuentas_procesadas}")
    print(f"   ❌ Cuentas sin procesar: {cuentas_sin_procesar}")
    print(f"   📄 Reportes nuevos a insertar: {len(registros)}")
    
    if registros:
        supabase.table("meta_ads_reportes_semanales").insert(registros).execute()
        print(f"✅ Se insertaron {len(registros)} reportes semanales.")
        return len(registros)
    else:
        print("ℹ️ No se insertaron registros. Ya existen para esta semana.")
        return 0

if __name__ == "__main__":
    sincronizar_reportes_semanales()
