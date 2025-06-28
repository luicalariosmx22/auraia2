#!/usr/bin/env python3
"""
🧹 Limpiador de Historial para Probar Bienvenida
Permite resetear el historial de un usuario para probar la bienvenida personalizada
"""

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

def verificar_historial_usuario(telefono):
    """Verifica el historial del usuario"""
    try:
        historial = supabase.table("historial_conversaciones") \
            .select("id, timestamp, mensaje, tipo") \
            .eq("telefono", telefono) \
            .eq("nombre_nora", "aura") \
            .order("timestamp", desc=True) \
            .limit(10) \
            .execute()
        
        if historial.data:
            print(f"📊 HISTORIAL ENCONTRADO para {telefono}:")
            print(f"   Total mensajes: {len(historial.data)}")
            
            for i, msg in enumerate(historial.data[:5], 1):
                timestamp = msg.get("timestamp", "")
                tipo = msg.get("tipo", "")
                mensaje_corto = msg.get("mensaje", "")[:50] + "..."
                print(f"   {i}. {timestamp} | {tipo} | {mensaje_corto}")
            
            # Verificar última interacción
            ultimo_msg = historial.data[0]
            timestamp_str = ultimo_msg["timestamp"]
            
            # Calcular días desde última interacción
            try:
                if isinstance(timestamp_str, str):
                    timestamp_str = timestamp_str.replace('Z', '').replace('+00:00', '')
                    if '.' in timestamp_str:
                        ultima_interaccion = datetime.fromisoformat(timestamp_str)
                    else:
                        ultima_interaccion = datetime.fromisoformat(timestamp_str)
                
                ahora = datetime.now()
                dias_inactivo = (ahora - ultima_interaccion).days
                
                print(f"\n⏰ ANÁLISIS TEMPORAL:")
                print(f"   Última interacción: {ultima_interaccion}")
                print(f"   Días inactivo: {dias_inactivo}")
                print(f"   ¿Debe enviar bienvenida? {'SÍ' if dias_inactivo >= 7 else 'NO'}")
                
            except Exception as e:
                print(f"❌ Error calculando tiempo: {e}")
            
        else:
            print(f"✅ NO HAY HISTORIAL para {telefono}")
            print("   → Enviará bienvenida personalizada en próximo mensaje")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def limpiar_historial_usuario(telefono, confirmar=False):
    """Limpia el historial de un usuario"""
    if not confirmar:
        print("⚠️ ADVERTENCIA: Esto eliminará TODO el historial del usuario")
        respuesta = input("¿Continuar? (escribe 'CONFIRMAR'): ")
        if respuesta != "CONFIRMAR":
            print("❌ Operación cancelada")
            return
    
    try:
        # Eliminar historial
        response = supabase.table("historial_conversaciones") \
            .delete() \
            .eq("telefono", telefono) \
            .eq("nombre_nora", "aura") \
            .execute()
        
        print(f"🧹 HISTORIAL ELIMINADO para {telefono}")
        print("✅ Próximo mensaje activará bienvenida personalizada")
        
    except Exception as e:
        print(f"💥 Error: {e}")

def simular_primera_vez(telefono):
    """Simula que es la primera vez que escribe el usuario"""
    print(f"🎭 SIMULANDO PRIMERA INTERACCIÓN para {telefono}")
    print("=" * 50)
    
    # 1. Verificar si es empleado
    response = supabase.table("usuarios_clientes") \
        .select("*") \
        .eq("telefono", telefono) \
        .eq("nombre_nora", "aura") \
        .execute()
    
    if response.data:
        usuario = response.data[0]
        print(f"✅ Usuario encontrado: {usuario['nombre']}")
        print(f"   Rol: {usuario['rol']}")
        print(f"   Tipo: usuario_cliente (empleado)")
        
        # 2. Verificar historial
        verificar_historial_usuario(telefono)
        
        # 3. Ofrecer limpiar historial
        print(f"\n🎯 PARA PROBAR BIENVENIDA PERSONALIZADA:")
        print(f"   1. Limpiar historial del usuario")
        print(f"   2. Enviar mensaje desde WhatsApp")
        print(f"   3. Debería recibir mensaje personalizado")
        
        limpiar = input("\n¿Limpiar historial ahora? (s/n): ").lower()
        if limpiar == 's':
            limpiar_historial_usuario(telefono, confirmar=True)
    else:
        print(f"❌ Usuario {telefono} no encontrado como empleado")

if __name__ == "__main__":
    telefono = "6629360887"
    
    print("🧹 VERIFICADOR/LIMPIADOR DE HISTORIAL")
    print("=" * 40)
    print("1. Verificar historial actual")
    print("2. Simular primera vez (con opción de limpiar)")
    print("3. Solo limpiar historial")
    
    opcion = input("\nSelecciona opción (1-3): ")
    
    if opcion == "1":
        verificar_historial_usuario(telefono)
    elif opcion == "2":
        simular_primera_vez(telefono)
    elif opcion == "3":
        limpiar_historial_usuario(telefono)
    else:
        print("Opción inválida")
