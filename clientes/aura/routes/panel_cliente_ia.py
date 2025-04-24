print("✅ panel_cliente_ia.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, session
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_ia_bp = Blueprint("panel_cliente_ia", __name__)

@panel_cliente_ia_bp.route("/panel_cliente/ia/<nombre_nora>", methods=["GET", "POST"])
def panel_ia(nombre_nora):
    user = session.get("user")
    if not user:
        return redirect(url_for("login.login_google"))

    # Cargar configuración desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"❌ Error al cargar configuración: {not response.data}")
            return f"❌ No se encontró la configuración para {nombre_nora}"
        config = response.data[0]
        print(f"✅ Configuración cargada: {config}")  # Depuración: Verificar configuración cargada
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración para {nombre_nora}"

    if request.method == "POST":
        # Obtener estado de IA y mensaje de bienvenida desde el formulario
        estado_nuevo = request.form.get("ia_activada") == "true"
        mensaje_bienvenida = request.form.get("mensaje_bienvenida", "").strip()
        config["ia_activada"] = estado_nuevo
        config["mensaje_bienvenida"] = mensaje_bienvenida
        print(f"🔄 Actualizando configuración: ia_activada={estado_nuevo}, mensaje_bienvenida={mensaje_bienvenida}")  # Depuración

        # Guardar configuración en Supabase
        try:
            response = supabase.table("configuracion_bot").update({
                "ia_activada": estado_nuevo,
                "mensaje_bienvenida": mensaje_bienvenida
            }).eq("nombre_nora", nombre_nora).execute()
            if not response.data:
                print(f"❌ Error al actualizar configuración: {not response.data}")
                return f"❌ Error al actualizar configuración para {nombre_nora}"
            print(f"✅ Configuración actualizada correctamente.")  # Depuración
        except Exception as e:
            print(f"❌ Error al actualizar configuración: {str(e)}")
            return f"❌ Error al actualizar configuración para {nombre_nora}"

        return redirect(url_for("panel_cliente_ia.panel_ia", nombre_nora=nombre_nora))

    # Obtener los bloques de conocimiento para esta Nora
    try:
        conocimientos = supabase.table("conocimiento_nora") \
            .select("id, titulo, contenido") \
            .eq("numero_nora", config["numero_nora"]) \
            .order("titulo") \
            .execute().data
        print(f"✅ Bloques de conocimiento cargados: {conocimientos}")  # Depuración: Verificar bloques cargados
    except Exception as e:
        print(f"❌ Error al cargar bloques de conocimiento: {e}")
        conocimientos = []

    # Renderizar la plantilla con los datos de configuración y bloques de conocimiento
    print(f"🔍 Renderizando plantilla con: ia_activada={config.get('ia_activada', True)}, mensaje_bienvenida={config.get('mensaje_bienvenida', '')}, conocimientos={len(conocimientos)} bloques")  # Depuración
    return render_template(
        "panel_cliente_ia.html",
        user=user,
        ia_activada=config.get("ia_activada", True),
        mensaje_bienvenida=config.get("mensaje_bienvenida", ""),
        nombre_nora=nombre_nora,
        conocimientos=conocimientos  # <- nuevo
    )

@panel_cliente_ia_bp.route("/panel_cliente/ia/<nombre_nora>/editar_conocimiento/<id>", methods=["POST"])
def editar_conocimiento(nombre_nora, id):
    """
    Edita un bloque de conocimiento específico.
    """
    titulo = request.form.get("titulo", "").strip()
    contenido = request.form.get("contenido", "").strip()
    try:
        supabase.table("conocimiento_nora").update({
            "titulo": titulo,
            "contenido": contenido
        }).eq("id", id).execute()
        print(f"✅ Bloque de conocimiento con ID {id} actualizado correctamente.")
    except Exception as e:
        print(f"❌ Error al editar conocimiento: {e}")
    return redirect(url_for("panel_cliente_ia.panel_ia", nombre_nora=nombre_nora))


@panel_cliente_ia_bp.route("/panel_cliente/ia/<nombre_nora>/borrar_conocimiento/<id>")
def borrar_conocimiento(nombre_nora, id):
    """
    Borra un bloque de conocimiento específico.
    """
    try:
        supabase.table("conocimiento_nora").delete().eq("id", id).execute()
        print(f"✅ Bloque de conocimiento con ID {id} eliminado correctamente.")
    except Exception as e:
        print(f"❌ Error al borrar conocimiento: {e}")
    return redirect(url_for("panel_cliente_ia.panel_ia", nombre_nora=nombre_nora))
