from flask import Blueprint, request, render_template, flash, redirect
import uuid
from supabase import create_client

# Configuración de Supabase
url = "https://your-supabase-url.supabase.co"
key = "your-supabase-key"
supabase = create_client(url, key)

registro_cliente_bp = Blueprint("registro_cliente_bp", __name__)

@registro_cliente_bp.route("/registro_cliente/<nombre_nora>", methods=["GET", "POST"])
def registro_cliente(nombre_nora):
    if request.method == "POST":
        nombre_cliente = request.form.get("nombre_cliente")
        tipo = request.form.get("tipo")
        telefono = request.form.get("telefono")
        email = request.form.get("email")
        ciudad = request.form.get("ciudad")
        nombre_empresa = request.form.get("nombre_empresa")

        cliente_data = {
            "id": str(uuid.uuid4()),
            "nombre_nora": nombre_nora,
            "nombre_cliente": nombre_cliente,
            "tipo": tipo,
            "telefono": telefono,
            "email": email,
            "ciudad": ciudad
        }
        result = supabase.table("clientes").insert(cliente_data).execute()

        if result.error or not result.data:
            flash("❌ Hubo un error al guardar tus datos. Intenta más tarde.", "error")
            return redirect(request.url)

        # También registrar la empresa (opcional)
        empresa_data = {
            "id": str(uuid.uuid4()),
            "nombre_nora": nombre_nora,
            "cliente_id": cliente_data["id"],
            "nombre_cliente": nombre_cliente,
            "nombre_empresa": nombre_empresa
        }
        supabase.table("cliente_empresas").insert(empresa_data).execute()

        return render_template("registro_cliente_gracias.html", nombre=nombre_cliente)

    return render_template("registro_cliente_form.html", nombre_nora=nombre_nora)