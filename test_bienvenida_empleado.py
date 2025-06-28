#!/usr/bin/env python3
"""
🧪 Test completo del sistema de bienvenida para empleados
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
from clientes.aura.handlers.process_message import identificar_tipo_contacto, generar_mensaje_bienvenida_empleado

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_identificacion_empleado():
    """Test de identificación de empleado"""
    print("🧪 TEST IDENTIFICACIÓN DE EMPLEADO")
    print("=" * 50)
    
    telefono = "6629360887"
    nombre_nora = "aura"
    
    # Probar identificación
    tipo_contacto = identificar_tipo_contacto(telefono, nombre_nora)
    
    print(f"📞 Teléfono: {telefono}")
    print(f"🤖 Nora: {nombre_nora}")
    print(f"👤 Tipo identificado: {tipo_contacto}")
    
    return tipo_contacto

def test_mensaje_bienvenida():
    """Test de generación de mensaje de bienvenida"""
    print("\n🧪 TEST MENSAJE DE BIENVENIDA")
    print("=" * 50)
    
    # Usar datos reales del empleado
    tipo_contacto = test_identificacion_empleado()
    
    if tipo_contacto["tipo"] == "usuario_cliente":
        print("✅ Usuario identificado como empleado")
        
        # Generar mensaje
        mensaje = generar_mensaje_bienvenida_empleado(tipo_contacto, "aura")
        
        print("\n📱 MENSAJE GENERADO:")
        print("-" * 30)
        print(mensaje)
        print("-" * 30)
        
    else:
        print(f"❌ Usuario NO identificado como empleado: {tipo_contacto['tipo']}")

def verificar_condiciones_bienvenida():
    """Verifica las condiciones para enviar bienvenida"""
    print("\n🧪 TEST CONDICIONES DE BIENVENIDA")
    print("=" * 50)
    
    telefono = "6629360887"
    nombre_nora = "aura"
    
    # Verificar historial
    historial = supabase.table("historial_conversaciones") \
        .select("id, timestamp") \
        .eq("telefono", telefono) \
        .eq("nombre_nora", nombre_nora) \
        .order("timestamp", desc=True) \
        .limit(1) \
        .execute().data
    
    print(f"📋 Historial encontrado: {len(historial)} registros")
    
    if historial:
        timestamp_str = historial[0]["timestamp"]
        print(f"🕒 Último timestamp: {timestamp_str}")
        
        try:
            # Manejar diferentes formatos de timestamp
            if isinstance(timestamp_str, str):
                timestamp_str = timestamp_str.replace('Z', '').replace('+00:00', '')
                if '.' in timestamp_str:
                    ultima_interaccion = datetime.fromisoformat(timestamp_str)
                else:
                    ultima_interaccion = datetime.fromisoformat(timestamp_str)
            
            ahora = datetime.now()
            dias_inactivo = (ahora - ultima_interaccion).days
            
            print(f"⏰ Días de inactividad: {dias_inactivo}")
            
            if dias_inactivo >= 7:
                print("✅ DEBE ENVIAR BIENVENIDA (inactivo >= 7 días)")
                return True
            else:
                print("❌ NO debe enviar bienvenida (activo reciente)")
                return False
                
        except Exception as e:
            print(f"❌ Error calculando inactividad: {e}")
            return False
    else:
        print("✅ DEBE ENVIAR BIENVENIDA (sin historial)")
        return True

def limpiar_historial_temporal():
    """Limpia el historial temporal para forzar bienvenida"""
    print("\n🧹 LIMPIAR HISTORIAL PARA FORZAR BIENVENIDA")
    print("=" * 50)
    
    telefono = "6629360887"
    nombre_nora = "aura"
    
    respuesta = input("¿Limpiar historial para forzar bienvenida? (s/n): ").lower()
    if respuesta == 's':
        try:
            # Eliminar historial
            response = supabase.table("historial_conversaciones") \
                .delete() \
                .eq("telefono", telefono) \
                .eq("nombre_nora", nombre_nora) \
                .execute()
            
            print(f"✅ Historial limpiado")
            print("💡 Ahora envía un mensaje desde WhatsApp para activar la bienvenida")
            
        except Exception as e:
            print(f"❌ Error limpiando historial: {e}")

def test_completo():
    """Test completo del sistema"""
    print("🚀 TEST COMPLETO SISTEMA BIENVENIDA EMPLEADOS")
    print("=" * 60)
    
    # 1. Identificación
    tipo_contacto = test_identificacion_empleado()
    
    # 2. Mensaje de bienvenida
    test_mensaje_bienvenida()
    
    # 3. Condiciones
    debe_enviar = verificar_condiciones_bienvenida()
    
    # 4. Resumen
    print("\n📊 RESUMEN")
    print("=" * 30)
    print(f"👤 Tipo: {tipo_contacto.get('tipo', 'desconocido')}")
    print(f"📩 Debe enviar bienvenida: {'SÍ' if debe_enviar else 'NO'}")
    
    if tipo_contacto.get("tipo") == "usuario_cliente" and debe_enviar:
        print("✅ SISTEMA LISTO - Debería enviar bienvenida personalizada")
    else:
        print("⚠️ Revisar configuración o condiciones")
    
    # 5. Opción de limpiar historial
    limpiar_historial_temporal()

if __name__ == "__main__":
    test_completo()
