from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from utils.validar_modulo_activo import modulo_activo_para_nora
from clientes.aura.utils.supabase_client import supabase

panel_cliente_clientes_bp = Blueprint('panel_cliente_clientes_bp', __name__)

@panel_cliente_clientes_bp.route("/")
def vista_clientes():
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for('login.login_screen'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Obtener todos los clientes de esta Nora
    clientes_data = supabase.table("clientes").select("*").eq("nombre_nora", nombre_nora).execute()
    clientes = clientes_data.data if clientes_data.data else []

    # ✅ Debug para verificar si se están recuperando
    print(f"🟡 [clientes] nombre_nora = {nombre_nora}")
    print(f"📦 Total encontrados: {len(clientes)}")
    if clientes:
        print("🔍 Primer cliente:", clientes[0])

    for cliente in clientes:
        # Empresas asociadas a este cliente
        empresas_data = supabase.table("cliente_empresas") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("cliente_id", cliente["id"]) \
            .execute()
        cliente["empresas"] = empresas_data.data if empresas_data.data else []

        for empresa in cliente["empresas"]:
            empresa["url_editar"] = url_for('panel_cliente_clientes_bp.editar_empresa', empresa_id=empresa["id"])
        cliente["url_nueva_ads"] = url_for('panel_cliente_clientes_bp.nueva_cuenta_ads', cliente_id=cliente["id"])

        # Cuentas publicitarias asociadas
        ads_data = supabase.table("meta_ads_cuentas") \
            .select("*") \
            .eq("cliente_id", cliente["id"]) \
            .execute()
        cliente["ads_cuentas"] = ads_data.data if ads_data.data else []

    return render_template('panel_cliente_clientes.html', nombre_nora=nombre_nora, clientes=clientes, user=session.get("user"))

@panel_cliente_clientes_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for("login.login_screen"))

    if not modulo_activo_para_nora(nombre_nora, "clientes"):
        return "Módulo no activo", 403

    if request.method == "POST":
        nombre_cliente = request.form.get("nombre_cliente", "").strip()
        tipo = request.form.get("tipo", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip()
        nombre_empresa = request.form.get("nombre_empresa", "").strip()

        # Validación
        if not nombre_cliente or not tipo or not email or not telefono or not nombre_empresa:
            flash("❌ Todos los campos son obligatorios", "error")
            return redirect(request.url)

        # Insertar cliente
        cliente_data = {
            "nombre_nora": nombre_nora,
            "nombre_cliente": nombre_cliente,
            "tipo": tipo,
            "email": email,
            "telefono": telefono
        }

        resultado_cliente = supabase.table("clientes").insert(cliente_data).execute()
        if not resultado_cliente.data:
            flash("❌ Error al guardar el cliente", "error")
            return redirect(request.url)

        cliente_id = resultado_cliente.data[0]["id"]

        # Insertar empresa vinculada
        empresa_data = {
            "nombre_nora": nombre_nora,
            "nombre_cliente": nombre_cliente,
            "cliente_id": cliente_id,
            "nombre_empresa": nombre_empresa
        }
        supabase.table("cliente_empresas").insert(empresa_data).execute()

        flash("✅ Cliente y empresa guardados correctamente", "success")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    return render_template("panel_cliente_clientes_nuevo.html", nombre_nora=nombre_nora, user=session.get("user"))

# ----------- EMPRESAS: Formulario edit / share -----------------

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/editar", methods=["GET", "POST"])
def editar_empresa(empresa_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for('login.login_screen'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Cargar empresa
    empresa_resp = supabase.table("cliente_empresas").select("*").eq("id", empresa_id).single().execute()
    empresa = empresa_resp.data

    if not empresa:
        return "Empresa no encontrada", 404

    if request.method == "POST":
        campos = {
            "nombre_empresa": request.form.get("nombre_empresa"),
            "giro": request.form.get("giro"),
            "telefono_empresa": request.form.get("telefono_empresa"),
            "email_empresa": request.form.get("email_empresa"),
            "sitio_web": request.form.get("sitio_web")
        }
        supabase.table("cliente_empresas").update(campos).eq("id", empresa_id).execute()
        flash("Empresa actualizada", "success")
        return redirect(url_for('panel_cliente_clientes_bp.vista_clientes'))

    return render_template('panel_cliente_empresa_form.html', nombre_nora=nombre_nora, empresa=empresa, user=session.get("user"))

# ----------- VINCULAR CUENTA ADS -----------------

@panel_cliente_clientes_bp.route("/cliente/<cliente_id>/ads/nueva", methods=["GET", "POST"])
def nueva_cuenta_ads(cliente_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for('login.login_screen'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Validar cliente
    cli = supabase.table("clientes").select("id,nombre_cliente").eq("id", cliente_id).single().execute()
    if cli.error or not cli.data:
        return "Cliente no encontrado", 404
    cliente = cli.data

    if request.method == "POST":
        cuenta_data = {
            "id": str(uuid.uuid4()),
            "cliente_id": cliente_id,
            "nombre_nora": nombre_nora,
            "tipo_plataforma": request.form.get("tipo_plataforma"),
            "ad_account_id": request.form.get("ad_account_id"),
            "nombre_cuenta": request.form.get("nombre_cuenta"),
            "activo": True
        }
        supabase.table("meta_ads_cuentas").insert(cuenta_data).execute()
        flash("Cuenta publicitaria vinculada", "success")
        return redirect(url_for('panel_cliente_clientes_bp.vista_clientes'))

    return render_template('panel_cliente_vincular_ads.html', nombre_nora=nombre_nora, cliente=cliente, user=session.get("user"))
