from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from utils.validar_modulo_activo import modulo_activo_para_nora
from clientes.aura.utils.supabase_client import supabase

panel_cliente_clientes_bp = Blueprint('panel_cliente_clientes_bp', __name__)

@panel_cliente_clientes_bp.route("/")
def vista_clientes():
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for("login.login_screen"))

    if not modulo_activo_para_nora(nombre_nora, "clientes"):
        return "Módulo no activo", 403

    # Obtener todos los clientes de esta Nora
    clientes_data = supabase.table("clientes").select("*").eq("nombre_nora", nombre_nora).execute()
    clientes = clientes_data.data if clientes_data.data else []

    for cliente in clientes:
        # Empresas asociadas
        empresas_data = supabase.table("cliente_empresas") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("cliente_id", cliente["id"]) \
            .execute()
        cliente["empresas"] = empresas_data.data if empresas_data.data else []

        for empresa in cliente["empresas"]:
            empresa["url_editar"] = url_for("panel_cliente_clientes_bp.editar_empresa", empresa_id=empresa["id"])
        cliente["url_nueva_ads"] = url_for("panel_cliente_clientes_bp.nueva_cuenta_ads", cliente_id=cliente["id"])

    return render_template(
        "panel_cliente_clientes.html",
        nombre_nora=nombre_nora,
        clientes=clientes,
        user=session.get("user"),
        modulo_activo="clientes"  # ✅ esto activa el menú correcto
    )

@panel_cliente_clientes_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for("login.login_screen"))

    if not modulo_activo_para_nora(nombre_nora, "clientes"):
        return "Módulo no activo", 403

    if request.method == "POST":
        nombre_cliente = request.form.get("nombre_cliente", "").strip()
        email = request.form.get("email", "").strip()

        # Validación mínima
        if not nombre_cliente or not email:
            flash("❌ El nombre y el correo electrónico son obligatorios", "error")
            return redirect(request.url)

        cliente_data = {
            "nombre_nora": nombre_nora,
            "nombre_cliente": request.form.get("nombre_cliente", "").strip(),
            "email": request.form.get("email", "").strip(),
            "telefono": request.form.get("telefono", "").strip() or None,
            "tipo": request.form.get("tipo", "").strip() or None,
            "ciudad": request.form.get("ciudad", "").strip() or None,
            "estado": request.form.get("estado", "").strip() or None,
            "pais": request.form.get("pais", "").strip() or None,
            "puesto": request.form.get("puesto", "").strip() or None,
            "genero": request.form.get("genero", "").strip() or None,
            "cumple": request.form.get("cumple") or None,
            "notas": request.form.get("notas", "").strip() or None,
            "medio_contact": request.form.get("medio_contact", "").strip() or None,
            "acepta_promo": request.form.get("acepta_promo") == "on"
        }

        # Insertar cliente
        resultado = supabase.table("clientes").insert(cliente_data).execute()
        if not resultado.data:
            flash("❌ Error al guardar el cliente", "error")
            return redirect(request.url)

        flash("✅ Cliente guardado correctamente", "success")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    return render_template("panel_cliente_clientes_nuevo.html",
                          nombre_nora=nombre_nora,
                          user=session.get("user"),
                          modulo_activo="clientes")

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

    return render_template("panel_cliente_empresa_form.html",
                          nombre_nora=nombre_nora,
                          empresa=empresa,
                          user=session.get("user"),
                          modulo_activo="clientes")

@panel_cliente_clientes_bp.route("/empresa/nueva", methods=["GET", "POST"])
def nueva_empresa():
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for("login.login_screen"))

    if request.method == "POST":
        nombre_empresa = request.form.get("nombre_empresa", "").strip()
        if not nombre_empresa:
            flash("❌ El nombre de la empresa es obligatorio", "error")
            return redirect(request.url)

        empresa_data = {
            "id": str(uuid.uuid4()),
            "nombre_nora": nombre_nora,
            "nombre_empresa": nombre_empresa,
            "giro": request.form.get("giro", "").strip(),
            "telefono_empresa": request.form.get("telefono_empresa", "").strip(),
            "email_empresa": request.form.get("email_empresa", "").strip(),
            "sitio_web": request.form.get("sitio_web", "").strip(),
            "direccion": request.form.get("direccion", "").strip(),
            "ciudad": request.form.get("ciudad", "").strip(),
            "estado": request.form.get("estado", "").strip(),
            "pais": request.form.get("pais", "").strip(),
            "cp": request.form.get("cp", "").strip(),
            "facebook": request.form.get("facebook", "").strip(),
            "instagram": request.form.get("instagram", "").strip(),
            "whatsapp": request.form.get("whatsapp", "").strip(),
            "pagina_web": request.form.get("pagina_web", "").strip(),
            "notas": request.form.get("notas", "").strip(),
            "activo": True
        }

        supabase.table("cliente_empresas").insert(empresa_data).execute()
        flash("✅ Empresa creada correctamente", "success")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    return render_template("panel_cliente_empresa_nueva.html",
                          nombre_nora=nombre_nora,
                          user=session.get("user"),
                          modulo_activo="clientes")

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/ligar_cliente", methods=["GET", "POST"])
def ligar_cliente(empresa_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for("login.login_screen"))

    # Cargar empresa
    empresa_resp = supabase.table("cliente_empresas").select("*").eq("id", empresa_id).single().execute()
    empresa = empresa_resp.data
    if not empresa:
        flash("❌ Empresa no encontrada", "error")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        if cliente_id:
            supabase.table("cliente_empresas").update({
                "cliente_id": cliente_id
            }).eq("id", empresa_id).execute()
            flash("✅ Cliente vinculado correctamente", "success")
            return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    # Obtener clientes activos de esta Nora
    clientes = supabase.table("clientes").select("id, nombre_cliente") \
        .eq("nombre_nora", nombre_nora).execute().data or []

    return render_template("ligar_cliente_empresa.html",
                          empresa=empresa,
                          clientes=clientes,
                          nombre_nora=nombre_nora,
                          modulo_activo="clientes")

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

# ----------- LIGAR EMPRESA A CLIENTE -----------------

@panel_cliente_clientes_bp.route("/cliente/<cliente_id>/ligar_empresa", methods=["GET", "POST"])
def ligar_empresa(cliente_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for("login.login_screen"))

    # Obtener cliente actual
    cliente_resp = supabase.table("clientes").select("*").eq("id", cliente_id).single().execute()
    if not cliente_resp.data:
        flash("❌ Cliente no encontrado", "error")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))
    cliente = cliente_resp.data

    # Si se envía el formulario para vincular
    if request.method == "POST":
        empresa_id = request.form.get("empresa_id")
        if empresa_id:
            supabase.table("cliente_empresas").update({
                "cliente_id": cliente_id
            }).eq("id", empresa_id).execute()
            flash("✅ Empresa ligada correctamente", "success")
            return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    # Obtener empresas no ligadas
    empresas_disp = supabase.table("cliente_empresas").select("*") \
        .eq("nombre_nora", nombre_nora).is_("cliente_id", "null").execute().data or []

    # Enriquecer empresas con cliente si existe
    for empresa in empresas_disp:
        if empresa.get("cliente_id"):
            cliente_resp = supabase.table("clientes").select("id, nombre_cliente").eq("id", empresa["cliente_id"]).single().execute()
            empresa["cliente"] = cliente_resp.data

    return render_template("ligar_empresa_cliente.html",
                          cliente=cliente,
                          empresas=empresas_disp,
                          nombre_nora=nombre_nora,
                          modulo_activo="clientes")

@panel_cliente_clientes_bp.route("/empresas", methods=["GET"])
def vista_empresas():
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for("login.login_screen"))

    # Obtener empresas de esta Nora
    empresas = supabase.table("cliente_empresas") \
        .select("*") \
        .eq("nombre_nora", nombre_nora) \
        .execute().data or []

    # Agregar info del cliente si está ligada
    for empresa in empresas:
        if empresa.get("cliente_id"):
            cliente = supabase.table("clientes") \
                .select("id, nombre_cliente") \
                .eq("id", empresa["cliente_id"]) \
                .single().execute().data
            empresa["cliente"] = cliente
        empresa["url_editar"] = url_for("panel_cliente_clientes_bp.editar_empresa", empresa_id=empresa["id"])
        empresa["url_ligar"] = url_for("panel_cliente_clientes_bp.ligar_cliente", empresa_id=empresa["id"], nombre_nora=nombre_nora)

    return render_template("panel_cliente_empresas.html",
                           nombre_nora=nombre_nora,
                           empresas=empresas,
                           modulo_activo="clientes",
                           user=session.get("user"))

@panel_cliente_clientes_bp.route("/cliente/<cliente_id>/editar", methods=["GET", "POST"])
def editar_cliente(cliente_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("user"):
        return redirect(url_for('login.login_screen'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Buscar cliente
    response = supabase.table("clientes").select("*").eq("id", cliente_id).single().execute()
    cliente = response.data

    if not cliente:
        flash("❌ Cliente no encontrado", "error")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    if request.method == "POST":
        campos = {
            "nombre_cliente": request.form.get("nombre_cliente", "").strip(),
            "email": request.form.get("email", "").strip(),
            "telefono": request.form.get("telefono", "").strip() or None,
            "tipo": request.form.get("tipo", "").strip() or None,
            "ciudad": request.form.get("ciudad", "").strip() or None,
            "estado": request.form.get("estado", "").strip() or None,
            "pais": request.form.get("pais", "").strip() or None,
            "puesto": request.form.get("puesto", "").strip() or None,
            "genero": request.form.get("genero", "").strip() or None,
            "cumple": request.form.get("cumple") or None,
            "notas": request.form.get("notas", "").strip() or None,
            "medio_contact": request.form.get("medio_contact", "").strip() or None,
            "acepta_promo": request.form.get("acepta_promo") == "on"
        }
        supabase.table("clientes").update(campos).eq("id", cliente_id).execute()
        flash("✅ Cliente actualizado correctamente", "success")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    return render_template("panel_cliente_cliente_editar.html",
                           cliente=cliente,
                           nombre_nora=nombre_nora,
                           user=session.get("user"),
                           modulo_activo="clientes")
