print("✅ panel_cliente.py cargado correctamente")

from flask import Blueprint, render_template, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os
import datetime

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def es_ruta_valida(ruta):
    return isinstance(ruta, str) and "panel_cliente/" in ruta

def serializar_config(obj):
    if isinstance(obj, dict):
        return {k: serializar_config(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serializar_config(i) for i in obj]
    elif isinstance(obj, (datetime.timedelta, datetime.datetime)):
        return str(obj)
    else:
        return obj

def crear_blueprint_panel_cliente(nombre_nora):
    bp = Blueprint(f"panel_cliente_{nombre_nora}", __name__)

    @bp.route("/")
    def configuracion_cliente():
        print(f"🧪 Entrando a configuracion_cliente de {nombre_nora}")

        if not session.get("email"):
            return redirect(url_for("simple_login_unique.login_simple"))

        try:
            # 1. Configuración de la Nora
            result = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
            config = result.data[0] if result.data else {}

            # 2. Leer módulos activos
            raw_modulos = config.get("modulos", [])
            if isinstance(raw_modulos, str):
                modulos_activos = [m.strip() for m in raw_modulos.split(",")]
            else:
                modulos_activos = raw_modulos

            # 3. Traer definiciones desde modulos_disponibles
            resultado_def = supabase.table("modulos_disponibles").select("*").execute()
            modulos_definidos = resultado_def.data or []

            modulos_dict = {
                m.get("nombre", "").strip().lower(): {
                    "nombre": m.get("nombre", "").strip(),
                    "ruta": m.get("ruta", "").strip() if es_ruta_valida(m.get("ruta", "")) else "",
                    "icono": m.get("icono", ""),
                    "descripcion": m.get("descripcion", "")
                }
                for m in modulos_definidos
            }

            # 4. Filtrar solo los módulos activos y definidos
            modulos_disponibles = sorted([
                {
                    "nombre": modulos_dict[nombre.lower()]["nombre"].replace("_", " ").capitalize(),
                    "ruta": f"/panel_cliente/{nombre_nora}/{nombre.lower()}",
                    "icono": modulos_dict[nombre.lower()]["icono"] or "🧩",
                    "descripcion": modulos_dict[nombre.lower()]["descripcion"] or "Módulo activo"
                }
                for nombre in modulos_activos
                if nombre.lower() in modulos_dict
            ], key=lambda x: x["nombre"].lower())

            print("✅ Módulos visibles para panel:", modulos_disponibles)

            # 🛠 Flags para acceso rápido en el template
            modulos_activos_flags = {m.lower(): True for m in modulos_activos}
            modulo_clientes = 'clientes' in [m.lower() for m in modulos_activos]

        except Exception as e:
            print(f"❌ Error en configuracion_cliente: {str(e)}")
            config = {}
            modulos_disponibles = []
            modulos_activos_flags = {}
            modulo_clientes = False

        config_serializado = serializar_config(config)

        return render_template(
            "panel_cliente.html",
            nombre_nora=nombre_nora,
            nombre_visible=nombre_nora.capitalize(),
            user=session.get("user", {"name": "Usuario"}),
            modulos=modulos_disponibles,
            modulos_activos=modulos_activos_flags,
            modulo_clientes=modulo_clientes
        )

    # 👉 Asegura que se pasen los módulos activos al template del panel
    @bp.route("/panel_cliente/<nombre_nora>")
    def panel_cliente_dashboard(nombre_nora):
        config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).single().execute().data
        modulos = config.get("modulos", [])
        return render_template("panel_cliente/index.html", nombre_nora=nombre_nora, modulos=modulos)

    # 👉 Nueva ruta para estadísticas de Nora
    @bp.route("/panel_cliente/<nombre_nora>/estadisticas_nora")
    def estadisticas_nora(nombre_nora):
        try:
            # Obtener estadísticas de mensajes del historial
            mensajes_response = supabase.table("historial_conversaciones").select("*").eq("nora", nombre_nora).execute()
            mensajes = mensajes_response.data if mensajes_response.data else []
            
            # Calcular estadísticas básicas
            total_mensajes = len(mensajes)
            
            # Contar mensajes enviados vs recibidos
            mensajes_enviados = len([m for m in mensajes if m.get('tipo') == 'enviado'])
            mensajes_recibidos = len([m for m in mensajes if m.get('tipo') == 'recibido'])
            
            # Usuarios únicos (números de teléfono únicos)
            usuarios_unicos = len(set([m.get('telefono') for m in mensajes if m.get('telefono')]))
            
            # Obtener conversaciones activas (últimas 24h)
            from datetime import datetime, timedelta
            hace_24h = datetime.now() - timedelta(hours=24)
            conversaciones_24h = len([m for m in mensajes if m.get('created_at') and m.get('created_at') > hace_24h.isoformat()])
            
            # Mensajes por día (últimos 7 días)
            estadisticas_diarias = {}
            for i in range(7):
                fecha = datetime.now() - timedelta(days=i)
                fecha_str = fecha.strftime('%Y-%m-%d')
                estadisticas_diarias[fecha_str] = len([
                    m for m in mensajes 
                    if m.get('created_at') and m.get('created_at').startswith(fecha_str)
                ])
            
            # Horarios de mayor actividad
            horarios_actividad = {}
            for mensaje in mensajes:
                if mensaje.get('created_at'):
                    try:
                        hora = datetime.fromisoformat(mensaje['created_at'].replace('Z', '+00:00')).hour
                        horarios_actividad[hora] = horarios_actividad.get(hora, 0) + 1
                    except:
                        continue
            
            estadisticas = {
                'total_mensajes': total_mensajes,
                'mensajes_enviados': mensajes_enviados,
                'mensajes_recibidos': mensajes_recibidos,
                'usuarios_unicos': usuarios_unicos,
                'conversaciones_24h': conversaciones_24h,
                'estadisticas_diarias': estadisticas_diarias,
                'horarios_actividad': horarios_actividad
            }
            
            print(f"✅ Estadísticas de {nombre_nora}: {estadisticas}")
            
            return render_template("estadisticas_nora.html", 
                                 nombre_nora=nombre_nora, 
                                 estadisticas=estadisticas)
                                 
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de {nombre_nora}: {e}")
            return render_template("estadisticas_nora.html", 
                                 nombre_nora=nombre_nora, 
                                 estadisticas={
                                     'total_mensajes': 0,
                                     'mensajes_enviados': 0,
                                     'mensajes_recibidos': 0,
                                     'usuarios_unicos': 0,
                                     'conversaciones_24h': 0,
                                     'estadisticas_diarias': {},
                                     'horarios_actividad': {}
                                 },
                                 error=str(e))

    return bp
