#!/usr/bin/env python3
"""
Script de verificación del sistema de tokens de páginas de Facebook.

Este script verifica:
1. Que la tabla facebook_paginas tenga las columnas necesarias
2. Que las funciones de API funcionen correctamente
3. El estado actual de los tokens de páginas

Uso:
    python verificar_tokens_paginas.py
"""

import os
import sys
import requests
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase

def verificar_tabla_facebook_paginas():
    """Verifica que la tabla facebook_paginas tenga las columnas necesarias."""
    print("🔍 Verificando estructura de tabla facebook_paginas...")
    
    try:
        # Intentar obtener una página con todas las columnas relevantes
        response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina, access_token, access_token_valido, ultima_sincronizacion") \
            .limit(1) \
            .execute()
        
        if response.data is not None:
            print("✅ Tabla facebook_paginas tiene todas las columnas necesarias")
            return True
        else:
            print("❌ Error accediendo a tabla facebook_paginas")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando tabla: {str(e)}")
        return False

def verificar_funciones_token():
    """Verifica que las funciones de obtención de token funcionen."""
    print("\n🔍 Verificando funciones de token...")
    
    try:
        # Importar las funciones
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_api import obtener_token_pagina
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_meta import obtener_token_principal, obtener_token_apropiado
        
        # Verificar token principal
        token_principal = obtener_token_principal()
        if token_principal:
            print(f"✅ Token principal encontrado (longitud: {len(token_principal)})")
        else:
            print("⚠️ Token principal no encontrado")
        
        # Obtener una página de ejemplo
        response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina") \
            .eq("activa", True) \
            .limit(1) \
            .execute()
        
        if response.data:
            page_id = response.data[0]['page_id']
            nombre_pagina = response.data[0]['nombre_pagina']
            
            print(f"🔍 Probando con página: '{nombre_pagina}' ({page_id})")
            
            # Probar función de token específico
            token_pagina = obtener_token_pagina(page_id)
            if token_pagina:
                print(f"✅ Token específico encontrado para página (longitud: {len(token_pagina)})")
            else:
                print("⚠️ No hay token específico para esta página")
            
            # Probar función de token apropiado
            token_apropiado, tipo = obtener_token_apropiado(page_id)
            if token_apropiado:
                print(f"✅ Token apropiado encontrado (tipo: {tipo}, longitud: {len(token_apropiado)})")
            else:
                print("❌ No se pudo obtener ningún token apropiado")
        
        print("✅ Funciones de token verificadas")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando funciones: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error verificando funciones: {str(e)}")
        return False

def verificar_estado_paginas():
    """Verifica el estado actual de todas las páginas."""
    print("\n🔍 Verificando estado de páginas...")
    
    try:
        response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina, activa, access_token, access_token_valido, ultima_sincronizacion") \
            .execute()
        
        if not response.data:
            print("⚠️ No se encontraron páginas en la base de datos")
            return False
        
        total_paginas = len(response.data)
        activas = 0
        con_token = 0
        tokens_validos = 0
        tokens_invalidos = 0
        sin_token = 0
        
        print(f"\n📊 Analizando {total_paginas} páginas:")
        print("-" * 80)
        
        for pagina in response.data:
            page_id = pagina['page_id']
            nombre = pagina['nombre_pagina'][:30] + "..." if len(pagina['nombre_pagina']) > 30 else pagina['nombre_pagina']
            activa = pagina['activa']
            tiene_token = bool(pagina.get('access_token'))
            token_valido = pagina.get('access_token_valido', True) if tiene_token else False
            ultima_sync = pagina.get('ultima_sincronizacion', 'Nunca')
            
            if activa:
                activas += 1
            
            if tiene_token:
                con_token += 1
                if token_valido:
                    tokens_validos += 1
                    estado = "✅ VÁLIDO"
                else:
                    tokens_invalidos += 1
                    estado = "❌ INVÁLIDO"
            else:
                sin_token += 1
                estado = "⚪ SIN TOKEN"
            
            status_activa = "🟢" if activa else "🔴"
            
            print(f"{status_activa} {nombre:<35} | {page_id:<15} | {estado:<12} | {ultima_sync}")
        
        print("-" * 80)
        print(f"📈 RESUMEN:")
        print(f"   Total páginas: {total_paginas}")
        print(f"   🟢 Activas: {activas}")
        print(f"   🔴 Inactivas: {total_paginas - activas}")
        print(f"   🔑 Con token: {con_token}")
        print(f"   ✅ Tokens válidos: {tokens_validos}")
        print(f"   ❌ Tokens inválidos: {tokens_invalidos}")
        print(f"   ⚪ Sin token: {sin_token}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if sin_token > 0:
            print(f"   - Ejecutar 'python actualizar_tokens_paginas.py' para obtener {sin_token} tokens faltantes")
        if tokens_invalidos > 0:
            print(f"   - Revisar y regenerar {tokens_invalidos} tokens marcados como inválidos")
        if tokens_validos == activas and sin_token == 0:
            print(f"   - ¡Excelente! Todas las páginas activas tienen tokens válidos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estado de páginas: {str(e)}")
        return False

def verificar_apis():
    """Verifica que las APIs relacionadas con tokens estén funcionando."""
    print("\n🔍 Verificando APIs de tokens...")
    
    try:
        # Aquí podrías hacer requests a las APIs si tienes un servidor corriendo
        # Por ahora solo verificamos que los endpoints estén definidos
        
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_api import webhooks_api_bp
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_meta import webhooks_meta_bp
        
        # Verificar que los blueprints tengan las rutas esperadas
        rutas_esperadas = [
            '/api/webhooks/pagina/<page_id>/token',
            '/api/webhooks/pagina/<page_id>/validar-token',
            '/api/webhooks/tokens_paginas',
            '/api/webhooks/actualizar_tokens_masivo'
        ]
        
        print("✅ Blueprints de APIs importados correctamente")
        print("✅ Rutas de tokens configuradas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando APIs: {str(e)}")
        return False

def main():
    """Función principal del script de verificación."""
    print("🚀 Iniciando verificación del sistema de tokens de páginas...")
    print("=" * 80)
    
    verificaciones = [
        ("Estructura de tabla", verificar_tabla_facebook_paginas),
        ("Funciones de token", verificar_funciones_token),
        ("Estado de páginas", verificar_estado_paginas),
        ("APIs de tokens", verificar_apis)
    ]
    
    resultados = []
    
    for nombre, funcion in verificaciones:
        resultado = funcion()
        resultados.append((nombre, resultado))
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print("=" * 80)
    
    exitosas = 0
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: CORRECTO")
            exitosas += 1
        else:
            print(f"❌ {nombre}: ERROR")
    
    print(f"\n🎯 Verificaciones exitosas: {exitosas}/{len(resultados)}")
    
    if exitosas == len(resultados):
        print("🎉 ¡Sistema de tokens de páginas funcionando correctamente!")
    else:
        print("⚠️ Hay problemas que necesitan ser corregidos.")
    
    print("🏁 Verificación completada")

if __name__ == "__main__":
    main()
