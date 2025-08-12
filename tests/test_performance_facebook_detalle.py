#!/usr/bin/env python3
"""
🚀 TEST PERFORMANCE: Medir tiempo de carga de detalle_pagina_facebook
Identifica cuellos de botella en la función
"""

import os
import time
from supabase.client import create_client

def test_performance_detalle_pagina():
    """Mide el tiempo de cada consulta para identificar cuellos de botella"""
    
    # 🔗 Conexión directa a Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    page_id = "782681001814242"  # La página que tarda en cargar
    
    print(f"🔍 Midiendo performance para página {page_id}")
    
    # ⏱️ MEDICIÓN 1: Datos básicos de la página
    start_time = time.time()
    pagina_response = supabase.table('facebook_paginas').select('*').eq('page_id', page_id).single().execute()
    pagina_time = time.time() - start_time
    print(f"📄 Datos básicos página: {pagina_time:.3f}s")
    
    if not pagina_response.data:
        print("❌ Página no encontrada")
        return
    
    pagina = pagina_response.data
    
    # ⏱️ MEDICIÓN 2: Información de empresa
    start_time = time.time()
    if pagina.get('empresa_id'):
        empresa_response = supabase.table('cliente_empresas').select('id, nombre_empresa, cliente_id').eq('id', pagina['empresa_id']).single().execute()
        if empresa_response.data and empresa_response.data.get('cliente_id'):
            cliente_response = supabase.table('clientes').select('nombre_cliente').eq('id', empresa_response.data['cliente_id']).single().execute()
    empresa_time = time.time() - start_time
    print(f"🏢 Datos empresa: {empresa_time:.3f}s")
    
    # ⏱️ MEDICIÓN 3: 50 Publicaciones (POTENCIAL CUELLO DE BOTELLA)
    start_time = time.time()
    publicaciones_response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).order('created_time', desc=True).limit(50).execute()
    publicaciones_time = time.time() - start_time
    publicaciones_count = len(publicaciones_response.data) if publicaciones_response.data else 0
    print(f"📝 50 Publicaciones ({publicaciones_count} encontradas): {publicaciones_time:.3f}s")
    
    # ⏱️ MEDICIÓN 4: 50 Comentarios (POTENCIAL CUELLO DE BOTELLA)
    start_time = time.time()
    comentarios_response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'comment').order('created_time', desc=True).limit(50).execute()
    comentarios_time = time.time() - start_time
    comentarios_count = len(comentarios_response.data) if comentarios_response.data else 0
    print(f"💬 50 Comentarios ({comentarios_count} encontrados): {comentarios_time:.3f}s")
    
    # ⏱️ MEDICIÓN 5: 50 Reacciones (POTENCIAL CUELLO DE BOTELLA)
    start_time = time.time()
    reacciones_response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'reaction').order('created_time', desc=True).limit(50).execute()
    reacciones_time = time.time() - start_time
    reacciones_count = len(reacciones_response.data) if reacciones_response.data else 0
    print(f"👍 50 Reacciones ({reacciones_count} encontradas): {reacciones_time:.3f}s")
    
    # ⏱️ MEDICIÓN 6: Todas las empresas para el modal
    start_time = time.time()
    clientes_response = supabase.table('cliente_empresas').select('id, nombre_empresa, cliente_id').execute()
    clientes_time = time.time() - start_time
    clientes_count = len(clientes_response.data) if clientes_response.data else 0
    print(f"🏬 Todas las empresas ({clientes_count} encontradas): {clientes_time:.3f}s")
    
    # 📊 TIEMPO TOTAL
    total_time = pagina_time + empresa_time + publicaciones_time + comentarios_time + reacciones_time + clientes_time
    print(f"\n⏱️ TIEMPO TOTAL ESTIMADO: {total_time:.3f}s")
    
    # 🎯 RECOMENDACIONES
    print(f"\n🎯 ANÁLISIS DE PERFORMANCE:")
    if publicaciones_time > 1.0:
        print(f"   🚨 CUELLO DE BOTELLA: Publicaciones ({publicaciones_time:.3f}s)")
    if comentarios_time > 1.0:
        print(f"   🚨 CUELLO DE BOTELLA: Comentarios ({comentarios_time:.3f}s)")
    if reacciones_time > 1.0:
        print(f"   🚨 CUELLO DE BOTELLA: Reacciones ({reacciones_time:.3f}s)")
    if clientes_time > 0.5:
        print(f"   ⚠️ OPTIMIZABLE: Carga de empresas ({clientes_time:.3f}s)")
    
    print(f"\n💡 RECOMENDACIONES:")
    print(f"   • Reducir límite de 50 a 10 elementos iniciales")
    print(f"   • Usar campos específicos en SELECT en lugar de '*'")
    print(f"   • Implementar lazy loading para datos no críticos")
    print(f"   • Cache empresas en frontend")
    
    return total_time

if __name__ == "__main__":
    tiempo_total = test_performance_detalle_pagina()
    if tiempo_total > 5:
        print(f"🚨 CRÍTICO: Página muy lenta ({tiempo_total:.3f}s)")
    elif tiempo_total > 2:
        print(f"⚠️ MEJORABLE: Página algo lenta ({tiempo_total:.3f}s)")
    else:
        print(f"✅ ACEPTABLE: Página rápida ({tiempo_total:.3f}s)")
