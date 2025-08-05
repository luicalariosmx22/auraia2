"""
Test simple para verificar la funcionalidad de compartir reportes Meta Ads
Ejecutar: python test_compartir_simple.py
"""

def verificar_archivos_existentes():
    """Verifica que todos los archivos necesarios existan"""
    import os
    
    archivos_requeridos = [
        'clientes/aura/routes/panel_cliente_meta_ads/reportes.py',
        'clientes/aura/templates/panel_cliente_meta_ads/reportes.html',
        'clientes/aura/templates/panel_cliente_meta_ads/detalle_reporte_ads.html',
        'clientes/aura/templates/panel_cliente_meta_ads/detalle_reporte_publico.html',
        'meta_ads_reportes_compartidos.sql'
    ]
    
    print("🔍 Verificando archivos necesarios...")
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} - NO ENCONTRADO")
    
    return True

def verificar_rutas_en_reportes():
    """Verifica que las rutas estén definidas en reportes.py"""
    try:
        with open('clientes/aura/routes/panel_cliente_meta_ads/reportes.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        rutas_requeridas = [
            '/compartir_reporte',
            '/reporte_publico/<token_uuid>',
            '/api/reporte_publico/<token_uuid>/validar'
        ]
        
        print("\n🛣️  Verificando rutas en reportes.py...")
        
        for ruta in rutas_requeridas:
            if ruta in contenido:
                print(f"  ✅ {ruta}")
            else:
                print(f"  ❌ {ruta} - NO ENCONTRADA")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar rutas: {e}")
        return False

def verificar_javascript_templates():
    """Verifica que el JavaScript esté actualizado en los templates"""
    templates = [
        'clientes/aura/templates/panel_cliente_meta_ads/reportes.html',
        'clientes/aura/templates/panel_cliente_meta_ads/detalle_reporte_ads.html'
    ]
    
    print("\n🌐 Verificando JavaScript en templates...")
    
    for template in templates:
        try:
            with open(template, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            if '/compartir_reporte' in contenido:
                print(f"  ✅ {template} - URL actualizada")
            elif '/estadisticas/compartir_reporte' in contenido:
                print(f"  ⚠️  {template} - Usando URL antigua")
            else:
                print(f"  ❌ {template} - No se encontró función de compartir")
                
        except Exception as e:
            print(f"  ❌ {template} - Error: {e}")

def mostrar_resumen():
    """Muestra un resumen de la implementación"""
    print("\n" + "="*60)
    print("📋 RESUMEN DE IMPLEMENTACIÓN - COMPARTIR REPORTES META ADS")
    print("="*60)
    
    print("""
🎯 RUTAS IMPLEMENTADAS:
  • POST /panel_cliente/{nombre_nora}/meta_ads/compartir_reporte
  • GET  /panel_cliente/{nombre_nora}/meta_ads/reporte_publico/{uuid}?token={token}
  • GET  /panel_cliente/{nombre_nora}/meta_ads/api/reporte_publico/{uuid}/validar?token={token}

🎨 TEMPLATES ACTUALIZADOS:
  • reportes.html - Botón compartir con modal Bootstrap
  • detalle_reporte_ads.html - Botón compartir en vista detallada
  • detalle_reporte_publico.html - Vista pública responsive

🗄️  BASE DE DATOS:
  • Tabla: meta_ads_reportes_compartidos
  • Script SQL: meta_ads_reportes_compartidos.sql
  • Ejecutar en Supabase SQL Editor

🔗 FORMATO DE ENLACE GENERADO:
  https://app.soynoraai.com/panel_cliente/{nora}/meta_ads/reporte_publico/{uuid}?token={token}

📱 FUNCIONALIDADES:
  • Generación de enlaces únicos con token de seguridad
  • Modal con opciones de compartir (WhatsApp, Email, Copiar)
  • Vista pública responsive con exportar PDF
  • Validación de enlaces activos
  • Auditoría de enlaces compartidos

⚡ PARA USAR:
  1. Ejecutar script SQL en Supabase
  2. Reiniciar servidor Flask
  3. Ir a reportes Meta Ads
  4. Hacer clic en "🔗 Compartir"
  5. Copiar/compartir enlace generado
    """)

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DE FUNCIONALIDAD COMPARTIR REPORTES")
    print("="*60)
    
    try:
        verificar_archivos_existentes()
        verificar_rutas_en_reportes()
        verificar_javascript_templates()
        mostrar_resumen()
        
        print("\n✅ Verificación completada!")
        print("💡 Si todo está correcto, ejecuta el script SQL y reinicia el servidor.")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
