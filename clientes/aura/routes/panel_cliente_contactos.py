print("✅ panel_cliente_contactos.py cargado correctamente")

from flask import Blueprint, render_template, session, request, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_contactos_bp = Blueprint("panel_cliente_contactos", __name__)

@panel_cliente_contactos_bp.route("/<nombre_nora>", methods=["GET", "POST"])
def panel_contactos(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        response = supabase.table("contactos").select(
            "id, nombre, telefono, correo, empresa, rfc, direccion, ciudad, cumpleanos, notas, ultimo_mensaje"
        ).eq("nombre_nora", nombre_nora).execute()
        contactos = response.data if response.data else []

        etiquetas_response = supabase.table("etiquetas").select("id, nombre, color").eq("nombre_nora", nombre_nora).eq("activa", True).execute()
        etiquetas = etiquetas_response.data if etiquetas_response.data else []

        relacion_response = supabase.table("contacto_etiquetas").select("contacto_id, etiqueta_id").eq("nombre_nora", nombre_nora).execute()
        relaciones = relacion_response.data or []

        etiquetas_dict = {e["id"]: e for e in etiquetas}
        etiquetas_por_contacto = {}
        for rel in relaciones:
            contacto_id = rel["contacto_id"]
            etiqueta_id = rel["etiqueta_id"]
            etiquetas_por_contacto.setdefault(contacto_id, []).append(etiquetas_dict.get(etiqueta_id, {}))

        for contacto in contactos:
            contacto["etiquetas"] = etiquetas_por_contacto.get(contacto["id"], [])

        return render_template(
            "panel_cliente_contactos.html",
            nombre_nora=nombre_nora,
            contactos=contactos,
            etiquetas=etiquetas,
            user=session["user"]
        )
    except Exception as e:
        print(f"❌ Error al cargar contactos para {nombre_nora}: {str(e)}")
        return render_template(
            "panel_cliente_contactos.html",
            nombre_nora=nombre_nora,
            contactos=[],
            etiquetas=[],
            user=session["user"]
        )

@panel_cliente_contactos_bp.route("/<nombre_nora>/agregar", methods=["POST"])
def agregar_contacto(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        data = {
            "nombre_nora": nombre_nora,
            "telefono": request.form.get("telefono"),
            "nombre": request.form.get("nombre"),
            "correo": request.form.get("correo"),
            "celular": request.form.get("celular"),
            "empresa": request.form.get("empresa"),
            "rfc": request.form.get("rfc"),
            "direccion": request.form.get("direccion"),
            "ciudad": request.form.get("ciudad"),
            "cumpleanos": request.form.get("cumpleanos"),
            "notas": request.form.get("notas")
        }
        supabase.table("contactos").insert(data).execute()
        print(f"✅ Contacto agregado: {data}")
    except Exception as e:
        print(f"❌ Error al agregar contacto: {str(e)}")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/<nombre_nora>/acciones", methods=["POST"])
def acciones_contactos(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

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

@panel_cliente_contactos_bp.route("/<nombre_nora>/editar/<telefono>", methods=["GET", "POST"])
def editar_contacto(nombre_nora, telefono):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if request.method == "POST":
        try:
            data = {
                "nombre": request.form.get("nombre"),
                "correo": request.form.get("correo"),
                "celular": request.form.get("celular"),
                "empresa": request.form.get("empresa"),
                "rfc": request.form.get("rfc"),
                "direccion": request.form.get("direccion"),
                "ciudad": request.form.get("ciudad"),
                "cumpleanos": request.form.get("cumpleanos"),
                "notas": request.form.get("notas")
            }
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
            user=session["user"]
        )
    except Exception as e:
        print(f"❌ Error al cargar contacto para edición: {str(e)}")
        return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

print("✅ Blueprint de contactos cargado como '/contactos'")