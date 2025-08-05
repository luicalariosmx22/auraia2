"""
Sistema de notificaciones para alertas
Envía correos electrónicos y WhatsApp cuando se generan alertas críticas
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from datetime import datetime

def enviar_email_alerta(alerta_data, destinatario_email):
    """
    Envía un correo electrónico con la información de la alerta
    Usa las variables ya configuradas en .env.local
    """
    try:
        # Usar las variables que ya están en .env.local
        smtp_server = os.getenv('EMAIL_HOST')  # mail.soynoraai.com
        smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '465'))  # 465
        email_usuario = os.getenv('EMAIL_FROM')  # tareas@soynoraai.com
        email_password = os.getenv('EMAIL_PASSWORD')  # 1002ivimyH!
        
        if not all([smtp_server, email_usuario, email_password]):
            print("❌ Credenciales de email no encontradas en .env.local")
            print(f"📧 Verificar: EMAIL_HOST={smtp_server}, EMAIL_FROM={email_usuario}")
            return False
        
        # Type assertions para satisfacer el type checker
        smtp_server_str = str(smtp_server)
        email_usuario_str = str(email_usuario) 
        email_password_str = str(email_password)
        
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = email_usuario_str
        msg['To'] = destinatario_email
        msg['Subject'] = f"🚨 Alerta: {alerta_data.get('nombre', 'Alerta del Sistema')}"
        
        # Cuerpo del mensaje
        cuerpo = f"""
        <html>
        <body>
            <h2>🚨 Nueva Alerta del Sistema</h2>
            <p><strong>Nombre:</strong> {alerta_data.get('nombre', 'Sin nombre')}</p>
            <p><strong>Descripción:</strong> {alerta_data.get('descripcion', 'Sin descripción')}</p>
            <p><strong>Tipo:</strong> {alerta_data.get('tipo', 'general')}</p>
            <p><strong>Prioridad:</strong> {alerta_data.get('prioridad', 'media')}</p>
            <p><strong>Empresa:</strong> {alerta_data.get('datos', {}).get('empresa_nombre', 'No especificada')}</p>
            <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <hr>
            <p><em>Este es un mensaje automático del sistema de alertas AuraAI.</em></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(cuerpo, 'html'))
        
        # Usar SSL para puerto 465
        server = smtplib.SMTP_SSL(smtp_server_str, smtp_port)
        server.login(email_usuario_str, email_password_str)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email enviado a {destinatario_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False

def enviar_whatsapp_alerta(alerta_data, numero_telefono):
    """
    Envía un mensaje de WhatsApp con la información de la alerta usando Twilio
    Usa Message Template para evitar el error de ventana de 24 horas
    """
    try:
        # Configuración de Twilio - usando las variables que ya tienes en .env.local
        twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([twilio_sid, twilio_token, twilio_phone]):
            print("❌ Credenciales de Twilio no configuradas completamente")
            return False
        
        # Asegurar que el número de Twilio tenga el prefijo 'whatsapp:'
        if twilio_phone and not twilio_phone.startswith('whatsapp:'):
            twilio_phone = f"whatsapp:{twilio_phone}"
        
        # Asegurar que el número de destino tenga el prefijo 'whatsapp:'
        if not numero_telefono.startswith('whatsapp:'):
            # Limpiar y formatear el número
            numero_limpio = numero_telefono.replace('+', '').replace('-', '').replace(' ', '')
            # Si no tiene código de país, asumir México (+52)
            if len(numero_limpio) == 10:
                numero_limpio = f"52{numero_limpio}"
            elif len(numero_limpio) == 11 and numero_limpio.startswith('1'):
                numero_limpio = f"52{numero_limpio}"
            numero_telefono = f"whatsapp:+{numero_limpio}"
        
        client = Client(twilio_sid, twilio_token)
        
        # Enviar mensaje directo sin template
        try:
            # Mensaje conciso: solo título y empresa
            nombre_alerta = alerta_data.get('nombre', 'Nueva alerta')
            empresa_nombre = alerta_data.get('datos', {}).get('empresa_nombre', 'Sin empresa')
            
            mensaje_simple = f"🚨 {nombre_alerta}\n📊 {empresa_nombre}"
            
            message = client.messages.create(
                body=mensaje_simple,
                from_=twilio_phone,
                to=numero_telefono
            )
            
            print(f"✅ WhatsApp enviado a {numero_telefono} - SID: {message.sid}")
            print(f"📱 Mensaje: {mensaje_simple}")
            return True
            
        except Exception as error:
            print(f"❌ Error al enviar WhatsApp: {error}")
            return False
        
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp: {e}")
        return False

def enviar_notificaciones_alerta(alerta_data, configuraciones):
    """
    Envía notificaciones según las configuraciones (ahora soporta múltiples)
    """
    if not configuraciones:
        print("❌ No hay configuraciones de notificación")
        return []
    
    # Si es una sola configuración (compatibilidad con versión anterior)
    if isinstance(configuraciones, dict):
        configuraciones = [configuraciones]
    
    notificaciones_enviadas = []
    
    # Número fijo para WhatsApp (tu número personal) - enviar solo una vez
    NUMERO_WHATSAPP_ADMIN = "+526629360887"  # Tu número personal correcto
    whatsapp_admin_enviado = False
    
    for config in configuraciones:
        print(f"📤 Enviando notificaciones para: {config.get('nombre_nora')}")
        
        # Verificar si debe enviar según prioridad
        solo_alta = config.get('solo_alta_prioridad', False)  # Cambiar a False para enviar todas
        prioridad_alerta = alerta_data.get('prioridad', 'media')
        
        if solo_alta and prioridad_alerta != 'alta':
            print(f"⏭️ Saltando notificación - solo alta prioridad habilitada y alerta es '{prioridad_alerta}'")
            continue
        
        # Enviar email al cliente
        if config.get('email_notificaciones', True) and config.get('email'):
            if enviar_email_alerta(alerta_data, config['email']):
                notificaciones_enviadas.append(f"email:{config['email']}")
    
    # Enviar WhatsApp al admin solo una vez, al final
    if configuraciones and not whatsapp_admin_enviado:
        if enviar_whatsapp_alerta(alerta_data, NUMERO_WHATSAPP_ADMIN):
            notificaciones_enviadas.append(f"whatsapp:{NUMERO_WHATSAPP_ADMIN}")
            whatsapp_admin_enviado = True
            print(f"✅ WhatsApp enviado al admin (una sola vez)")
    
    return notificaciones_enviadas

def obtener_configuracion_notificaciones_por_empresa(empresa_nombre):
    """
    Obtiene la configuración de notificaciones para una empresa específica
    Busca en la tabla cliente_empresas usando el nombre de la empresa
    """
    from clientes.aura.utils.supabase_client import supabase
    
    try:
        # Buscar la empresa en la tabla cliente_empresas
        response_empresa = supabase.table("cliente_empresas") \
            .select("*") \
            .eq("nombre_empresa", empresa_nombre) \
            .eq("activo", True) \
            .execute()
        
        if not response_empresa.data:
            print(f"❌ No se encontró la empresa '{empresa_nombre}' en cliente_empresas")
            return []
        
        empresa = response_empresa.data[0]
        print(f"✅ Empresa encontrada: {empresa.get('nombre_empresa')} - {empresa.get('nombre_nora')}")
        
        configuraciones = []
        
        # Crear configuración basada en los datos de la empresa
        config_empresa = {
            'nombre_nora': empresa.get('nombre_nora'),
            'email': empresa.get('email_empresa') or empresa.get('email_representante'),
            'telefono': empresa.get('telefono_empresa') or empresa.get('telefono_representante'),
            'email_notificaciones': True,  # Por defecto habilitado
            'whatsapp_notificaciones': True,    # Por defecto habilitado para WhatsApp
            'solo_alta_prioridad': False   # Enviar todas las alertas
        }
        
        if config_empresa['email'] or config_empresa['telefono']:
            configuraciones.append(config_empresa)
            print(f"📧 Configuración creada - Email: {config_empresa['email']}, WhatsApp: {config_empresa['telefono']}")
        
        # También buscar si hay configuración específica en configuracion_notificaciones
        if empresa.get('nombre_nora'):
            response_config = supabase.table("configuracion_notificaciones") \
                .select("*") \
                .eq("nombre_nora", empresa.get('nombre_nora')) \
                .execute()
            
            if response_config.data:
                configuraciones.extend(response_config.data)
                print(f"📧 Encontrada configuración adicional en configuracion_notificaciones")
        
        return configuraciones
            
    except Exception as e:
        print(f"❌ Error al obtener configuración de notificaciones: {e}")
        return []

def obtener_configuracion_notificaciones(nombre_nora):
    """
    Obtiene la configuración de notificaciones para un usuario específico
    Mantiene la función anterior para compatibilidad
    """
    from clientes.aura.utils.supabase_client import supabase
    
    try:
        # Buscar configuración principal
        response = supabase.table("configuracion_notificaciones") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        # También buscar configuración del cliente
        response_cliente = supabase.table("configuracion_notificaciones") \
            .select("*") \
            .eq("nombre_nora", f"{nombre_nora}_cliente") \
            .execute()
        
        configuraciones = []
        
        # Agregar configuración principal si existe
        if response.data:
            configuraciones.extend(response.data)
        
        # Agregar configuración del cliente si existe
        if response_cliente.data:
            configuraciones.extend(response_cliente.data)
        
        if configuraciones:
            print(f"📧 Encontradas {len(configuraciones)} configuraciones de notificación")
            return configuraciones
        else:
            # Configuración por defecto
            print("⚠️ No hay configuraciones de notificación")
            return []
            
    except Exception as e:
        print(f"❌ Error al obtener configuración de notificaciones: {e}")
        return []
