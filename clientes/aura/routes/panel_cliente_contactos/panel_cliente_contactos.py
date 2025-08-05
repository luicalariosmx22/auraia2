from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from supabase import create_client
from dotenv import load_dotenv
from clientes.aura.utils.login_required import login_required  # Añadir esta importación
import os
import uuid
import datetime
from dateutil import parser

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_contactos_bp = Blueprint(
    "panel_cliente_contactos", 
    __name__,
    template_folder="templates"
)

# El blueprint se registra en registro_dinamico.py con:
# safe_register_blueprint(app, panel_cliente_contactos_bp, url_prefix=f"/panel_cliente/{nombre_nora}/contactos")
@panel_cliente_contactos_bp.route("/", methods=["GET"])
@login_required
def vista_contactos():
    """Vista principal del panel de contactos."""
    try:
        # Obtener parámetros de la URL
        nombre_nora = request.path.split("/")[2]
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Construir consulta base
        query = supabase.table("contactos").select(
            "id, nombre, telefono, correo, empresa, rfc, direccion, ciudad, cumpleanos, notas, ultimo_mensaje, etiquetas_string",
            count="exact"
        ).eq("nombre_nora", nombre_nora)
        
        # Aplicar filtros si existen
        if request.args.get('filtro_nombre'):
            query = query.ilike('nombre', f"%{request.args.get('filtro_nombre')}%")
        if request.args.get('filtro_empresa'):
            query = query.ilike('empresa', f"%{request.args.get('filtro_empresa')}%")
        if request.args.get('filtro_etiqueta'):
            query = query.contains('etiquetas_string', request.args.get('filtro_etiqueta'))

        # Ejecutar consulta principal
        response = query.execute()
        total = response.count if hasattr(response, 'count') else 0
        
        # Aplicar paginación
        query = query.range((page-1)*per_page, page*per_page-1).order('ultimo_mensaje', desc=True)
        response = query.execute()
        contactos = response.data if response.data else []
        
        # Calcular páginas totales
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        # Obtener etiquetas activas
        etiquetas_response = supabase.table("etiquetas").select(
            "id, nombre, color"
        ).eq("nombre_nora", nombre_nora).eq("activa", True).execute()
        etiquetas = etiquetas_response.data if etiquetas_response.data else []

        return render_template(
            "panel_cliente_contactos/index.html",
            nombre_nora=nombre_nora,
            contactos=contactos,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            etiquetas=etiquetas,
            user={"name": session.get("name", "Usuario")},
            now=datetime.date.today()
        )

    except Exception as e:
        print(f"❌ Error al cargar panel de contactos: {str(e)}")
        flash("Error al cargar los contactos", "error")
        
        # Asegurarnos de pasar todas las variables necesarias incluso en caso de error
        return render_template(
            "panel_cliente_contactos/index.html",
            nombre_nora=nombre_nora if 'nombre_nora' in locals() else None,
            contactos=[],
            page=page if 'page' in locals() else 1,
            per_page=20,
            total=0,
            total_pages=1,
            etiquetas=[],
            user={"name": session.get("name", "Usuario")},
            now=datetime.date.today(),
            error=str(e)
        )

@panel_cliente_contactos_bp.route("/agregar", methods=["POST"])
def agregar_contacto(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    try:
        cumpleanos = request.form.get("cumpleanos")
        data = {
            "nombre_nora": nombre_nora,
            "telefono": request.form.get("telefono"),
            "nombre": request.form.get("nombre"),
            "correo": request.form.get("correo"),
            "empresa": request.form.get("empresa"),
            "rfc": request.form.get("rfc"),
            "direccion": request.form.get("direccion"),
            "ciudad": request.form.get("ciudad"),
            "notas": request.form.get("notas")
        }
        if cumpleanos:
            data["cumpleanos"] = cumpleanos

        # --- SINCRONIZAR ETIQUETAS ---
        etiquetas_string = request.form.get("etiquetas_string", "").strip()
        etiquetas = [e.strip() for e in etiquetas_string.split(",") if e.strip()]
        etiquetas_unicas = []
        for etq in etiquetas:
            if etq not in etiquetas_unicas:
                etiquetas_unicas.append(etq)
        etiquetas = etiquetas_unicas
        if etiquetas:
            # Buscar etiquetas existentes en catálogo
            existentes_resp = supabase.table("etiquetas").select("nombre").eq("nombre_nora", nombre_nora).in_("nombre", etiquetas).execute()
            existentes = set(e["nombre"] for e in (existentes_resp.data or []))
            nuevas = [e for e in etiquetas if e not in existentes]
            colores = [
                '#6366f1', '#10b981', '#f59e42', '#f43f5e', '#3b82f6', '#eab308', '#8b5cf6', '#ef4444', '#14b8a6', '#f472b6', '#a3e635', '#facc15', '#f87171', '#38bdf8', '#fbbf24', '#22d3ee', '#e879f9', '#4ade80', '#f472b6', '#fcd34d', '#818cf8', '#f43f5e', '#f59e42', '#10b981', '#6366f1'
            ]
            for idx, nueva in enumerate(nuevas):
                color = colores[idx % len(colores)]
                supabase.table("etiquetas").insert({
                    "nombre_nora": nombre_nora,
                    "nombre": nueva,
                    "color": color,
                    "activa": True
                }).execute()
            etiquetas_string_final = ", ".join(etiquetas)
        else:
            etiquetas_string_final = ""
        data["etiquetas_string"] = etiquetas_string_final

        supabase.table("contactos").insert(data).execute()
        print(f"✅ Contacto agregado: {data}")
    except Exception as e:
        print(f"❌ Error al agregar contacto: {str(e)}")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/acciones", methods=["POST"])
def acciones_contactos(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    try:
        accion = request.form.get("accion")
        contactos_seleccionados = request.form.getlist("contactos_seleccionados")

        if accion == "eliminar":
            for telefono in contactos_seleccionados:
                supabase.table("contactos").delete().eq("nombre_nora", nombre_nora).eq("telefono", telefono).execute()
            print(f"✅ Contactos eliminados: {contactos_seleccionados}")
        elif accion == "editar":
            if contactos_seleccionados:
                return redirect(url_for("panel_cliente_contactos.editar_contacto", nombre_nora=nombre_nora, telefono=contactos_seleccionados[0]))
    except Exception as e:
        print(f"❌ Error al realizar acción en contactos: {str(e)}")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/editar/<telefono>", methods=["GET", "POST"])
def editar_contacto(nombre_nora=None, telefono=None):
    # Fallback: extraer nombre_nora del path si no lo pasa Flask
    if nombre_nora is None:
        import re
        match = re.search(r"/panel_cliente/([^/]+)/contactos", request.path)
        if match:
            nombre_nora = match.group(1)
        else:
            return "Error: nombre_nora no encontrado en la ruta", 400

    if not session.get("email"):
        return redirect(url_for("login.login"))

    if request.method == "POST":
        try:
            cumpleanos = request.form.get("cumpleanos")
            data = {
                "nombre": request.form.get("nombre"),
                "correo": request.form.get("correo"),
                "empresa": request.form.get("empresa"),
                "rfc": request.form.get("rfc"),
                "direccion": request.form.get("direccion"),
                "ciudad": request.form.get("ciudad"),
                "notas": request.form.get("notas")
            }
            if cumpleanos:
                data["cumpleanos"] = cumpleanos
            supabase.table("contactos").update(data).eq("nombre_nora", nombre_nora).eq("telefono", telefono).execute()
            print(f"✅ Contacto actualizado: {data}")
        except Exception as e:
            print(f"❌ Error al actualizar contacto: {str(e)}")
        return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

    try:
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).eq("telefono", telefono).execute()
        contacto = response.data[0] if response.data else {}
        return render_template(
            "editar_contacto.html",
            nombre_nora=nombre_nora,
            contacto=contacto,
            user={"name": session.get("name", "Usuario")}
        )
    except Exception as e:
        print(f"❌ Error al cargar contacto para edición: {str(e)}")
        return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/contactos/asignar_etiqueta", methods=["POST"])
def asignar_etiqueta(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    contacto_id = request.form.get("contacto_id")
    etiqueta_id = request.form.get("etiqueta_id")

    print("➡️ Recibido para asignar:", contacto_id, etiqueta_id, nombre_nora)

    try:
        # Verificar si ya existe esa relación
        existe = supabase.table("contacto_etiquetas") \
            .select("id") \
            .eq("contacto_id", contacto_id) \
            .eq("etiqueta_id", etiqueta_id) \
            .execute()

        if existe.data:
            print("⚠️ La etiqueta ya está asignada al contacto.")
            flash("Etiqueta ya asignada.", "warning")
        else:
            # Insertar nueva relación
            supabase.table("contacto_etiquetas").insert({
                "id": str(uuid.uuid4()),
                "contacto_id": contacto_id,
                "etiqueta_id": etiqueta_id,
                "nombre_nora": nombre_nora
            }).execute()
            print("✅ Etiqueta asignada correctamente.")
            flash("Etiqueta asignada correctamente al contacto.", "success")

        # --- ACTUALIZAR etiquetas_string ---
        # Obtener todas las etiquetas actuales del contacto
        relaciones = supabase.table("contacto_etiquetas").select("etiqueta_id").eq("contacto_id", contacto_id).execute().data or []
        etiqueta_ids = [r["etiqueta_id"] for r in relaciones]
        if etiqueta_ids:
            etiquetas = supabase.table("etiquetas").select("nombre").in_("id", etiqueta_ids).execute().data or []
            etiquetas_nombres = [e["nombre"] for e in etiquetas]
            etiquetas_string = ", ".join(etiquetas_nombres)
        else:
            etiquetas_string = ""
        supabase.table("contactos").update({"etiquetas_string": etiquetas_string}).eq("id", contacto_id).execute()
    except Exception as e:
        print(f"❌ Error al asignar etiqueta: {str(e)}")
        flash("Error al asignar la etiqueta. Por favor, intenta de nuevo.", "error")

    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/contactos/quitar_etiqueta", methods=["POST"])
def quitar_etiqueta(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    contacto_id = request.form.get("contacto_id")
    etiqueta_id = request.form.get("etiqueta_id")

    print("➡️ Intentando quitar etiqueta:", etiqueta_id, "de contacto:", contacto_id)

    try:
        # Buscar primero si existe la relación
        existe = supabase.table("contacto_etiquetas") \
            .select("id") \
            .eq("contacto_id", contacto_id) \
            .eq("etiqueta_id", etiqueta_id) \
            .eq("nombre_nora", nombre_nora) \
            .execute()

        if not existe.data:
            print("⚠️ La etiqueta ya había sido eliminada o no estaba asignada.")
            flash("La etiqueta ya había sido eliminada.", "warning")
        else:
            supabase.table("contacto_etiquetas") \
                .delete() \
                .eq("contacto_id", contacto_id) \
                .eq("etiqueta_id", etiqueta_id) \
                .eq("nombre_nora", nombre_nora) \
                .execute()
            print("🗑 Etiqueta quitada correctamente del contacto.")
            flash("Etiqueta eliminada correctamente del contacto.", "success")

        # --- ACTUALIZAR etiquetas_string ---
        relaciones = supabase.table("contacto_etiquetas").select("etiqueta_id").eq("contacto_id", contacto_id).execute().data or []
        etiqueta_ids = [r["etiqueta_id"] for r in relaciones]
        if etiqueta_ids:
            etiquetas = supabase.table("etiquetas").select("nombre").in_("id", etiqueta_ids).execute().data or []
            etiquetas_nombres = [e["nombre"] for e in etiquetas]
            etiquetas_string = ", ".join(etiquetas_nombres)
        else:
            etiquetas_string = ""
        supabase.table("contactos").update({"etiquetas_string": etiquetas_string}).eq("id", contacto_id).execute()
    except Exception as e:
        print(f"❌ Error al quitar etiqueta: {str(e)}")
        flash("Error al quitar la etiqueta. Intenta de nuevo.", "error")

    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/nuevo_usuario", methods=["POST"])
def nuevo_usuario(nombre_nora=None):
    if nombre_nora is None:
        import re
        match = re.search(r"/panel_cliente/([^/]+)/contactos", request.path)
        if match:
            nombre_nora = match.group(1)
        else:
            return "Error: nombre_nora no encontrado en la ruta", 400
    if not session.get("email"):
        return redirect(url_for("login.login"))
    try:
        data = {
            "nombre_nora": nombre_nora,
            "telefono": request.form.get("telefono"),
            "nombre": request.form.get("nombre"),
            "correo": request.form.get("correo"),
            "empresa": request.form.get("empresa"),
            "rfc": request.form.get("rfc"),
            "direccion": request.form.get("direccion"),
            "ciudad": request.form.get("ciudad"),
            "cumpleanos": request.form.get("cumpleanos"),
            "notas": request.form.get("notas"),
            # Los campos imagen_perfil, mensaje_reciente, ultimo_mensaje se pueden dejar en null
        }
        supabase.table("contactos").insert(data).execute()
        flash("Usuario agregado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al agregar usuario: {str(e)}")
        flash("Error al agregar usuario", "error")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/historial/<telefono>", methods=["GET"])
def historial_conversaciones(nombre_nora=None, telefono=None):
    # Fallback: extraer nombre_nora del path si no lo pasa Flask
    if nombre_nora is None:
        import re
        match = re.search(r"/panel_cliente/([^/]+)/contactos", request.path)
        if match:
            nombre_nora = match.group(1)
        else:
            return {"error": "nombre_nora no encontrado en la ruta"}, 400

    if not session.get("email"):
        return {"error": "No autenticado"}, 401

    # Normalizar teléfono a últimos 10 dígitos
    telefono_10 = str(telefono)[-10:]
    try:
        # Buscar mensajes en historial_conversaciones por nombre_nora y teléfono (últimos 10 dígitos)
        response = supabase.table("historial_conversaciones") \
            .select("id, mensaje, timestamp, emisor, telefono") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        mensajes = [m for m in (response.data or []) if str(m.get("telefono", ""))[-10:] == telefono_10]
        mensajes.sort(key=lambda x: x.get("timestamp", ""))
        return {"mensajes": mensajes}
    except Exception as e:
        print(f"❌ Error al obtener historial: {str(e)}")
        return {"error": "Error al obtener historial"}, 500

@panel_cliente_contactos_bp.route("/api/contacto/<contacto_id>/etiquetas_string", methods=["POST"])
def api_actualizar_etiquetas_string(contacto_id):
    if not session.get("email"):
        return jsonify({"success": False, "error": "No autenticado"}), 401
    try:
        data = request.get_json()
        etiquetas_string = data.get("etiquetas_string", "").strip()
        # Obtener nombre_nora del contacto
        contacto_resp = supabase.table("contactos").select("nombre_nora").eq("id", contacto_id).execute()
        if not contacto_resp.data:
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404
        nombre_nora = contacto_resp.data[0]["nombre_nora"]
        # Procesar etiquetas: limpiar, quitar duplicados, crear en catálogo si no existen
        etiquetas = [e.strip() for e in etiquetas_string.split(",") if e.strip()]
        etiquetas_unicas = []
        for etq in etiquetas:
            if etq not in etiquetas_unicas:
                etiquetas_unicas.append(etq)
        etiquetas = etiquetas_unicas
        if etiquetas:
            # Buscar etiquetas existentes en catálogo
            existentes_resp = supabase.table("etiquetas").select("nombre").eq("nombre_nora", nombre_nora).in_("nombre", etiquetas).execute()
            existentes = set(e["nombre"] for e in (existentes_resp.data or []))
            nuevas = [e for e in etiquetas if e not in existentes]
            # Insertar nuevas etiquetas con color personalizado (ciclo de colores)
            colores = [
                '#6366f1', '#10b981', '#f59e42', '#f43f5e', '#3b82f6', '#eab308', '#8b5cf6', '#ef4444', '#14b8a6', '#f472b6', '#a3e635', '#facc15', '#f87171', '#38bdf8', '#fbbf24', '#22d3ee', '#e879f9', '#4ade80', '#f472b6', '#fcd34d', '#818cf8', '#f43f5e', '#f59e42', '#10b981', '#6366f1'
            ]
            for idx, nueva in enumerate(nuevas):
                color = colores[idx % len(colores)]
                supabase.table("etiquetas").insert({
                    "nombre_nora": nombre_nora,
                    "nombre": nueva,
                    "color": color,
                    "activa": True
                }).execute()
            etiquetas_string_final = ", ".join(etiquetas)
        else:
            etiquetas_string_final = ""
        supabase.table("contactos").update({"etiquetas_string": etiquetas_string_final}).eq("id", contacto_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al actualizar etiquetas_string: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@panel_cliente_contactos_bp.route("/etiquetas/<etiqueta_id>/editar", methods=["POST"])
def editar_etiqueta(nombre_nora, etiqueta_id):
    if not session.get("email"):
        return redirect(url_for("login.login"))
    nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
    nuevo_color = request.form.get("nuevo_color", "").strip()
    if not nuevo_nombre or not nuevo_color:
        flash("Nombre y color requeridos", "error")
        return redirect(request.referrer or url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))
    try:
        supabase.table("etiquetas").update({
            "nombre": nuevo_nombre,
            "color": nuevo_color
        }).eq("id", etiqueta_id).eq("nombre_nora", nombre_nora).execute()
        flash("Etiqueta actualizada", "success")
    except Exception as e:
        flash(f"Error al actualizar etiqueta: {str(e)}", "error")
    return redirect(request.referrer or url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/etiquetas/<etiqueta_id>/eliminar", methods=["POST"])
def eliminar_etiqueta(nombre_nora, etiqueta_id):
    if not session.get("email"):
        return redirect(url_for("login.login"))
    try:
        supabase.table("etiquetas").delete().eq("id", etiqueta_id).eq("nombre_nora", nombre_nora).execute()
        flash("Etiqueta eliminada", "success")
    except Exception as e:
        flash(f"Error al eliminar etiqueta: {str(e)}", "error")
    return redirect(request.referrer or url_for("panel_cliente_contactos.vista_contactos", nombre_nora=nombre_nora))

print("✅ Blueprint de contactos cargado como '/contactos'")

# Añadir alias para mantener compatibilidad
panel_contactos = vista_contactos

# Registrar el alias como una ruta adicional
panel_cliente_contactos_bp.add_url_rule(
    "/",
    endpoint="panel_contactos",
    view_func=panel_contactos
)