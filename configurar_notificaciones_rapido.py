"""
Configuración rápida para probar notificaciones
Solo inserta la configuración de usuario
"""

import sys
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase

# 🔧 CONFIGURA ESTOS VALORES:
NOMBRE_NORA = 'aura'  # ✅ Encontrado en diagnóstico
EMAIL_DESTINO = 'soynoraai@gmail.com'  # Tu email principal
TELEFONO = '+5216629360887'  # Tu celular

def buscar_email_cliente():
    """Busca el email del cliente en la base de datos"""
    try:
        print("🔍 Buscando email del cliente en la base de datos...")
        
        # Buscar en diferentes tablas donde podría estar el email del cliente
        tablas_buscar = ['clientes', 'usuarios', 'empresas', 'cuentas_publicitarias']
        
        for tabla in tablas_buscar:
            try:
                response = supabase.table(tabla) \
                    .select("email") \
                    .not_.is_("email", "null") \
                    .limit(5) \
                    .execute()
                
                if response.data:
                    emails = [row['email'] for row in response.data if row.get('email')]
                    if emails:
                        print(f"📧 Emails encontrados en {tabla}: {emails}")
                        return emails[0]  # Retornar el primer email encontrado
                        
            except Exception as e:
                print(f"⚠️ Tabla {tabla} no encontrada o sin acceso: {e}")
                continue
        
        print("⚠️ No se encontró email del cliente, usando solo tu email")
        return None
        
    except Exception as e:
        print(f"❌ Error al buscar email del cliente: {e}")
        return None

def configurar_notificaciones():
    """Inserta configuración para recibir notificaciones"""
    try:
        # Buscar email del cliente
        email_cliente = buscar_email_cliente()
        
        # Configuración principal (tu email + SMS)
        config_principal = {
            'nombre_nora': NOMBRE_NORA,
            'email_notificaciones': True,
            'sms_notificaciones': True,  # Habilitar SMS para ti
            'email': EMAIL_DESTINO,
            'telefono': TELEFONO,
            'solo_alta_prioridad': False
        }
        
        print(f"📝 Configurando notificaciones para: {NOMBRE_NORA}")
        print(f"📧 Email principal: {EMAIL_DESTINO}")
        print(f"📱 SMS: {TELEFONO}")
        
        # Insertar configuración principal
        response = supabase.table("configuracion_notificaciones") \
            .upsert(config_principal, on_conflict='nombre_nora') \
            .execute()
        
        print("✅ Configuración principal guardada!")
        
        # Si hay email del cliente, crear configuración adicional
        if email_cliente and email_cliente != EMAIL_DESTINO:
            config_cliente = {
                'nombre_nora': f"{NOMBRE_NORA}_cliente",
                'email_notificaciones': True,
                'sms_notificaciones': False,  # Solo email para cliente
                'email': email_cliente,
                'telefono': None,
                'solo_alta_prioridad': True  # Solo alertas importantes
            }
            
            print(f"📧 Configurando también para cliente: {email_cliente}")
            
            response_cliente = supabase.table("configuracion_notificaciones") \
                .upsert(config_cliente, on_conflict='nombre_nora') \
                .execute()
            
            print("✅ Configuración del cliente guardada!")
        
        print("\n🎯 CONFIGURACIÓN COMPLETADA!")
        print("📧 Recibirás notificaciones en:", EMAIL_DESTINO)
        print("📱 SMS en:", TELEFONO)
        if email_cliente:
            print("👤 Cliente recibirá en:", email_cliente)
        
        print("\n🚀 AHORA PUEDES:")
        print("1. Ir al panel de alertas")
        print("2. Hacer clic en el botón 📧 de cualquier alerta")
        print("3. ¡Recibir notificaciones por email y SMS!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CONFIGURACIÓN RÁPIDA DE NOTIFICACIONES")
    print("=" * 40)
    print(f"👤 Usuario: {NOMBRE_NORA}")
    print(f"📧 Email: {EMAIL_DESTINO}")
    print("\n⚠️ ¿Los datos son correctos? (s/n)")
    
    if input().lower() == 's':
        configurar_notificaciones()
    else:
        print("👋 Edita el archivo y cambia NOMBRE_NORA y EMAIL_DESTINO")
