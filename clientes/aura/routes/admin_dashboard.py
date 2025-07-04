# clientes/aura/routes/admin_dashboard.py
# 👉 Protege el dashboard con verificación de sesión

from flask import Blueprint, render_template, current_app, session, redirect, url_for
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.verificador_rutas_runtime import verificar_rutas_vs_html
from clientes.aura.middlewares.verificar_login import admin_login_required
import traceback
import os
import requests
from twilio.rest import Client

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

def verificar_saldo_twilio():
    """Verifica el saldo disponible en Twilio"""
    try:
        # Configurar cliente de Twilio
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            return {
                'error': 'Credenciales de Twilio no configuradas',
                'saldo': 0,
                'moneda': 'USD',
                'estado': 'ERROR'
            }
        
        client = Client(account_sid, auth_token)
        
        # Obtener información de la cuenta
        account = client.api.accounts(account_sid).fetch()
        
        # Obtener saldo
        balance = client.api.accounts(account_sid).balance.fetch()
        
        saldo_float = float(balance.balance)
        moneda = balance.currency
        
        # Determinar estado basado en saldo
        if saldo_float > 10:
            estado = 'BUENO'
        elif saldo_float > 5:
            estado = 'ADVERTENCIA'
        elif saldo_float > 0:
            estado = 'BAJO'
        else:
            estado = 'CRITICO'
        
        return {
            'saldo': saldo_float,
            'moneda': moneda,
            'estado': estado,
            'cuenta_nombre': account.friendly_name,
            'cuenta_estado': account.status
        }
        
    except Exception as e:
        print(f"❌ Error al verificar saldo de Twilio: {str(e)}")
        return {
            'error': str(e),
            'saldo': 0,
            'moneda': 'USD',
            'estado': 'ERROR'
        }

def verificar_creditos_openai():
    """Verifica el uso y límites de créditos de OpenAI"""
    try:
        import openai
        from datetime import datetime, timedelta
        import requests
        
        # Configurar API key
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            return {
                'error': 'API Key de OpenAI no configurada',
                'uso_actual': 0,
                'limite': 0,
                'estado': 'ERROR'
            }
        
        # Headers para las requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Obtener límites de uso (billing)
        # Nota: OpenAI cambió su API, ahora usa organization billing
        try:
            # Intentar obtener información de uso de los últimos 30 días
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Endpoint para obtener uso
            usage_url = "https://api.openai.com/v1/usage"
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(usage_url, headers=headers, params=params)
            
            if response.status_code == 200:
                usage_data = response.json()
                
                # Calcular uso total en dólares
                total_usage = 0
                if 'data' in usage_data:
                    for day_data in usage_data['data']:
                        total_usage += day_data.get('n_generated_tokens_total', 0) * 0.000001  # Estimación aproximada
                
                # Como OpenAI no expone límites directamente, usar estimaciones
                limite_estimado = 100  # $100 USD como límite por defecto
                porcentaje_usado = (total_usage / limite_estimado) * 100
                
                # Determinar estado basado en porcentaje usado
                if porcentaje_usado < 50:
                    estado = 'BUENO'
                elif porcentaje_usado < 75:
                    estado = 'ADVERTENCIA'
                elif porcentaje_usado < 90:
                    estado = 'BAJO'
                else:
                    estado = 'CRITICO'
                
                return {
                    'uso_actual': round(total_usage, 2),
                    'limite': limite_estimado,
                    'porcentaje_usado': round(porcentaje_usado, 1),
                    'estado': estado,
                    'periodo': '30 días'
                }
            
            else:
                # Fallback: simplemente verificar que la API key funcione
                test_response = requests.get(
                    "https://api.openai.com/v1/models", 
                    headers=headers
                )
                
                if test_response.status_code == 200:
                    return {
                        'uso_actual': 0,
                        'limite': 100,
                        'porcentaje_usado': 0,
                        'estado': 'BUENO',
                        'periodo': 'API Activa',
                        'note': 'Uso no disponible'
                    }
                else:
                    return {
                        'error': f'Error de API: {test_response.status_code}',
                        'uso_actual': 0,
                        'limite': 0,
                        'estado': 'ERROR'
                    }
        
        except Exception as api_error:
            print(f"❌ Error de API OpenAI: {str(api_error)}")
            return {
                'error': str(api_error),
                'uso_actual': 0,
                'limite': 0,
                'estado': 'ERROR'
            }
            
    except Exception as e:
        print(f"❌ Error al verificar créditos de OpenAI: {str(e)}")
        return {
            'error': str(e),
            'uso_actual': 0,
            'limite': 0,
            'estado': 'ERROR'
        }

@admin_dashboard_bp.route("/")
@admin_login_required
def dashboard_admin():
    # ✅ Verificación de login
    if "email" not in session or not session.get("is_admin"):
        return redirect(url_for("login.login"))

    print("✅ Entrando al dashboard_admin")

    total_noras = 0
    total_modulos = 0
    lista_noras = []

    # Obtener Noras desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("nombre_nora, ia_activa, modulos").execute()
        if response and response.data:
            total_noras = len(response.data)
            lista_noras = [
                {
                    "nombre": item.get("nombre_nora", "Sin nombre"),
                    "ia_activada": item.get("ia_activa", False),
                    "modulos": item.get("modulos", []) or []
                }
                for item in response.data
            ]
            print(f"✅ Total de Noras encontradas: {total_noras}")
        else:
            print("❌ No se encontraron Noras.")
    except Exception as e:
        print(f"❌ Error al obtener Noras: {str(e)}")
        traceback.print_exc()

    # Obtener errores desde Supabase
    # (Sección removida - ya no se muestra en el dashboard)

    # Obtener módulos disponibles
    try:
        mod_response = supabase.table("modulos_disponibles").select("id").execute()
        if mod_response and mod_response.data:
            total_modulos = len(mod_response.data)
            print(f"✅ Total de módulos: {total_modulos}")
    except Exception as e:
        print(f"❌ Error al contar módulos: {str(e)}")

    # Verificar saldo de Twilio
    twilio_info = verificar_saldo_twilio()
    print(f"✅ Información de Twilio: {twilio_info}")
    # twilio_info = {
    #     'saldo': 10.5,
    #     'moneda': 'USD',
    #     'estado': 'BUENO',
    #     'cuenta_nombre': 'Mi Cuenta Twilio',
    #     'cuenta_estado': 'activo'
    # }

    # Verificar créditos de OpenAI
    openai_info = verificar_creditos_openai()
    print(f"✅ Información de OpenAI: {openai_info}")
    # openai_info = {
    #     'uso_actual': 45.5,
    #     'limite': 100,
    #     'porcentaje_usado': 45.5,
    #     'estado': 'BUENO',
    #     'periodo': '30 días'
    # }

    print("✅ Mostrando admin_dashboard.html con datos")
    return render_template("admin_dashboard.html",
        total_noras=total_noras,
        total_modulos=total_modulos,
        noras=lista_noras,
        twilio_info=twilio_info,
        openai_info=openai_info
    )

@admin_dashboard_bp.route("/twilio/refresh")
@admin_login_required
def refresh_twilio_status():
    """Endpoint para refrescar el estado de Twilio via AJAX"""
    from clientes.aura.utils.twilio_sender import verificar_estado_twilio
    
    twilio_info = verificar_estado_twilio()
    
    return {
        "success": True,
        "data": twilio_info
    }

@admin_dashboard_bp.route("/openai/refresh")
@admin_login_required
def refresh_openai_status():
    """Endpoint para refrescar el estado de OpenAI via AJAX"""
    
    openai_info = verificar_creditos_openai()
    
    return {
        "success": True,
        "data": openai_info
    }

@admin_dashboard_bp.route("/estadisticas/<nombre_nora>")
@admin_login_required
def estadisticas_nora(nombre_nora):
    """Vista de estadísticas de una Nora específica"""
    try:
        # Obtener estadísticas de mensajes
        mensajes_stats = supabase.table("historial_conversaciones")\
            .select("*")\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        total_mensajes = len(mensajes_stats.data) if mensajes_stats.data else 0
        
        # Mensajes por tipo
        mensajes_enviados = 0
        mensajes_recibidos = 0
        usuarios_unicos = set()
        
        if mensajes_stats.data:
            for mensaje in mensajes_stats.data:
                if mensaje.get("tipo") == "enviado":
                    mensajes_enviados += 1
                else:
                    mensajes_recibidos += 1
                
                # Agregar usuario único
                if mensaje.get("telefono"):
                    usuarios_unicos.add(mensaje["telefono"])
        
        # Obtener configuración de la Nora
        nora_config = supabase.table("configuracion_bot")\
            .select("*")\
            .eq("nombre_nora", nombre_nora)\
            .execute()
        
        nora_info = nora_config.data[0] if nora_config.data else {}
        
        # Obtener errores relacionados
        errores_stats = supabase.table("logs_errores")\
            .select("*")\
            .ilike("descripcion", f"%{nombre_nora}%")\
            .execute()
        
        total_errores = len(errores_stats.data) if errores_stats.data else 0
        
        # Obtener mensajes de los últimos 7 días
        from datetime import datetime, timedelta
        hace_7_dias = datetime.now() - timedelta(days=7)
        
        mensajes_recientes = supabase.table("historial_conversaciones")\
            .select("*")\
            .eq("nombre_nora", nombre_nora)\
            .gte("created_at", hace_7_dias.isoformat())\
            .execute()
        
        mensajes_7_dias = len(mensajes_recientes.data) if mensajes_recientes.data else 0
        
        estadisticas = {
            "nombre_nora": nombre_nora,
            "total_mensajes": total_mensajes,
            "mensajes_enviados": mensajes_enviados,
            "mensajes_recibidos": mensajes_recibidos,
            "usuarios_unicos": len(usuarios_unicos),
            "total_errores": total_errores,
            "mensajes_7_dias": mensajes_7_dias,
            "nora_info": nora_info,
            "estado_ia": nora_info.get("ia_activa", False),
            "modulos_activos": nora_info.get("modulos", []) or []
        }
        
        print(f"✅ Estadísticas de {nombre_nora}: {estadisticas}")
        
        return render_template("admin_estadisticas_nora.html", 
                             estadisticas=estadisticas,
                             nombre_nora=nombre_nora)
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas de {nombre_nora}: {str(e)}")
        return render_template("admin_estadisticas_nora.html", 
                             estadisticas=None,
                             error=str(e),
                             nombre_nora=nombre_nora)

@admin_dashboard_bp.route("/debug/rutas")
def debug_rutas():
    rutas_erroneas = verificar_rutas_vs_html(current_app)
    return render_template("debug_rutas.html", rutas=rutas_erroneas)
