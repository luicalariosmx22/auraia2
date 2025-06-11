from flask import Blueprint, render_template, request, redirect, url_for, flash, session  # se importa session para controlar la autenticación
import uuid  # ✅ Fix: se importa para generar IDs con uuid.uuid4()

from utils.validar_modulo_activo import modulo_activo_para_nora
from clientes.aura.utils.supabase_client import supabase

panel_cliente_clientes_bp = Blueprint('panel_cliente_clientes_bp', __name__)

@panel_cliente_clientes_bp.route("/")

def vista_clientes():
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
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
        user={"name": session.get("name", "Usuario")},
        modulo_activo="clientes"  # ✅ esto activa el menú correcto
    )

@panel_cliente_clientes_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
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
                          user={"name": session.get("name", "Usuario")},

                          modulo_activo="clientes")

# ----------- EMPRESAS: Formulario edit / share -----------------

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/editar", methods=["GET", "POST"])
def editar_empresa(empresa_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
        return redirect(url_for('login.login_screen'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Cargar empresa
    empresa_resp = supabase.table("cliente_empresas").select("*").eq("id", empresa_id).single().execute()
    empresa = empresa_resp.data

    if not empresa:
        return "Empresa no encontrada", 404

    if request.method == "POST":
        import json
        import uuid
        campos = {
            "nombre_empresa": request.form.get("nombre_empresa"),
            "razon_social": request.form.get("razon_social"),
            "rfc": request.form.get("rfc"),
            "email_empresa": request.form.get("email_empresa"),
            "telefono_empresa": request.form.get("telefono_empresa"),
            "sitio_web": request.form.get("sitio_web"),
            # logo_url se asigna abajo
            "ubicacion": request.form.get("ubicacion"),
            "ciudad": request.form.get("ciudad"),
            "estado": request.form.get("estado"),
            "pais": request.form.get("pais"),
            "tipo": request.form.get("tipo"),
            "giro": request.form.get("giro"),
            "representante_legal": request.form.get("representante_legal"),
            "email_representante": request.form.get("email_representante"),
            "telefono_representante": request.form.get("telefono_representante"),
            "fecha_alta": request.form.get("fecha_alta") or None,
            "fecha_baja": request.form.get("fecha_baja") or None,
            "notas": request.form.get("notas"),
            "activo": True if request.form.get("activo") else False
        }
        logo_url = request.form.get("logo_url", "").strip() or None
        logo_file = request.files.get("logo_file")
        if logo_file and logo_file.filename:
            ext = logo_file.filename.rsplit('.', 1)[-1].lower()
            filename = f"empresas/{empresa_id}/logo_{uuid.uuid4()}.{ext}"
            file_bytes = logo_file.read()
            res = supabase.storage.from_('empresa-logos').upload(filename, file_bytes)
            if hasattr(res, 'error') and res.error:
                flash('Error al subir el logo: ' + str(res.error), 'danger')
                campos["logo_url"] = logo_url  # fallback a URL manual
            else:
                public_url = supabase.storage.from_('empresa-logos').get_public_url(filename)
                campos["logo_url"] = public_url
        else:
            campos["logo_url"] = logo_url
        supabase.table("cliente_empresas").update(campos).eq("id", empresa_id).execute()
        flash("Empresa actualizada", "success")
        return redirect(url_for('panel_cliente_clientes_bp.ficha_empresa', empresa_id=empresa_id))

    return render_template("panel_cliente_empresa_form.html",
                          nombre_nora=nombre_nora,
                          empresa=empresa,
                          user={"name": session.get("name", "Usuario")},
                          modulo_activo="clientes")

@panel_cliente_clientes_bp.route("/empresa/nueva", methods=["GET", "POST"])
def nueva_empresa():
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
        return redirect(url_for("login.login_screen"))

    if request.method == "POST":
        import uuid
        nombre_empresa = request.form.get("nombre_empresa", "").strip()
        if not nombre_empresa:
            flash("❌ El nombre de la empresa es obligatorio", "error")
            return redirect(request.url)
        logo_url = request.form.get("logo_url", "").strip() or None
        logo_file = request.files.get("logo_file")
        empresa_id = str(uuid.uuid4())
        if logo_file and logo_file.filename:
            ext = logo_file.filename.rsplit('.', 1)[-1].lower()
            filename = f"empresas/{empresa_id}/logo_{uuid.uuid4()}.{ext}"
            file_bytes = logo_file.read()
            res = supabase.storage.from_('empresa-logos').upload(filename, file_bytes)
            if hasattr(res, 'error') and res.error:
                flash('Error al subir el logo: ' + str(res.error), 'danger')
            else:
                logo_url = supabase.storage.from_('empresa-logos').get_public_url(filename)
        empresa_data = {
            "id": empresa_id,
            "nombre_nora": nombre_nora,
            "nombre_empresa": nombre_empresa,
            "razon_social": request.form.get("razon_social", "").strip() or None,
            "rfc": request.form.get("rfc", "").strip() or None,
            "email_empresa": request.form.get("email_empresa", "").strip() or None,
            "telefono_empresa": request.form.get("telefono_empresa", "").strip() or None,
            "sitio_web": request.form.get("sitio_web", "").strip() or None,
            "logo_url": logo_url,
            "ubicacion": request.form.get("ubicacion", "").strip() or None,
            "ciudad": request.form.get("ciudad", "").strip() or None,
            "estado": request.form.get("estado", "").strip() or None,
            "pais": request.form.get("pais", "").strip() or None,
            "tipo": request.form.get("tipo", "").strip() or None,
            "giro": request.form.get("giro", "").strip() or None,
            "representante_legal": request.form.get("representante_legal", "").strip() or None,
            "email_representante": request.form.get("email_representante", "").strip() or None,
            "telefono_representante": request.form.get("telefono_representante", "").strip() or None,
            "fecha_alta": request.form.get("fecha_alta") or None,
            "fecha_baja": request.form.get("fecha_baja") or None,
            "notas": request.form.get("notas", "").strip() or None,
            "activo": True if request.form.get("activo") else False
        }

        supabase.table("cliente_empresas").insert(empresa_data).execute()
        flash("✅ Empresa creada correctamente", "success")
        return redirect(url_for("panel_cliente_clientes_bp.vista_clientes", nombre_nora=nombre_nora))

    return render_template("panel_cliente_empresa_nueva.html",
                          nombre_nora=nombre_nora,
                          user={"name": session.get("name", "Usuario")},
                          modulo_activo="clientes")

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/ligar_cliente", methods=["GET", "POST"])
def ligar_cliente(empresa_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
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
    if not session.get("email"):
        return redirect(url_for('login.login_screen'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Validar cliente
    cli = supabase.table("clientes").select("id,nombre_cliente").eq("id", cliente_id).single().execute()
    if not cli.data:
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

    return render_template('panel_cliente_vincular_ads.html', nombre_nora=nombre_nora, cliente=cliente, user={"name": session.get("name", "Usuario")})

# ----------- LIGAR EMPRESA A CLIENTE -----------------

@panel_cliente_clientes_bp.route("/cliente/<cliente_id>/ligar_empresa", methods=["GET", "POST"])
def ligar_empresa(cliente_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
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
    if not session.get("email"):
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
                           user={"name": session.get("name", "Usuario")})

@panel_cliente_clientes_bp.route("/cliente/<cliente_id>/editar", methods=["GET", "POST"])
def editar_cliente(cliente_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
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
                           user={"name": session.get("name", "Usuario")},
                           modulo_activo="clientes")

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/ficha", methods=["GET"])
def ficha_empresa(empresa_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
        return redirect(url_for("login.login_screen"))

    empresa_resp = supabase.table("cliente_empresas").select("*").eq("id", empresa_id).single().execute()
    empresa = empresa_resp.data
    if not empresa:
        flash("❌ Empresa no encontrada", "error")
        return redirect(url_for("panel_cliente_clientes_bp.vista_empresas", nombre_nora=nombre_nora))

    # --- Consultar cliente ligado a la empresa (si existe) ---
    cliente = None
    cliente_id = empresa.get("cliente_id")
    if cliente_id:
        cliente_resp = supabase.table("clientes").select("id, nombre_cliente").eq("id", cliente_id).single().execute()
        cliente = cliente_resp.data
        empresa["cliente"] = cliente

    # --- Consultar accesos ligados a la empresa ---
    accesos = supabase.table("empresa_accesos").select("*").eq("empresa_id", empresa_id).execute().data or []

    # --- Consultar tareas ligadas a la empresa ---
    tareas = supabase.table("tareas").select("*").eq("empresa_id", empresa_id).eq("activo", True).execute().data or []

    # --- Consultar subtareas ligadas a la empresa ---
    subtareas = supabase.table("subtareas").select("*").eq("empresa_id", empresa_id).eq("activo", True).execute().data or []
    subtareas_por_tarea = {}
    for s in subtareas:
        subtareas_por_tarea.setdefault(s["tarea_padre_id"], []).append(s)
    # Asociar subtareas a cada tarea
    for t in tareas:
        t["subtareas"] = subtareas_por_tarea.get(t["id"], [])

    print('DEBUG tareas:', tareas)
    print('DEBUG subtareas:', subtareas)
    print('DEBUG tareas_activas:', [t for t in tareas if t.get('estatus') != 'completada'])
    print('DEBUG tareas_completadas:', [t for t in tareas if t.get('estatus') == 'completada'])

    # --- Consultar pagos ligados a la empresa ---
    pagos = supabase.table("pagos").select("*").eq("empresa_id", empresa_id).execute().data or []

    # --- Consultar usuarios ligados a la empresa (por nombre_nora) ---
    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    # --- Consultar cuentas publicitarias ligadas a la empresa o cliente ---
    cuentas_ads = []
    if cliente_id:
        cuentas_ads = supabase.table("meta_ads_cuentas").select("*").eq("cliente_id", cliente_id).execute().data or []

    # --- Consultar reuniones ligadas a la empresa ---
    reuniones = supabase.table("reuniones_clientes").select("*").eq("empresa_id", empresa_id).order("fecha_hora", desc=True).execute().data or []

    # --- Consultar documentos importantes ligados a la empresa ---
    documentos = supabase.table("empresa_documentos").select("*").eq("empresa_id", empresa_id).order("creado_en", desc=True).execute().data or []

    return render_template(
        "panel_cliente_empresa_ficha.html",
        empresa=empresa,
        nombre_nora=nombre_nora,
        user={"name": session.get("name", "Usuario")},
        modulo_activo="clientes",
        tareas=tareas,
        pagos=pagos,
        usuarios=usuarios,
        cuentas_ads=cuentas_ads,
        reuniones=reuniones,
        accesos=accesos,
        documentos=documentos
    )

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/registrar_reunion", methods=["POST"])
def registrar_reunion(empresa_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
        return redirect(url_for("login.login_screen"))

    # Obtener empresa y cliente ligado
    empresa_resp = supabase.table("cliente_empresas").select("*", "cliente_id").eq("id", empresa_id).single().execute()
    empresa = empresa_resp.data
    if not empresa:
        flash("❌ Empresa no encontrada", "error")
        return redirect(url_for("panel_cliente_clientes_bp.vista_empresas", nombre_nora=nombre_nora))
    cliente_id = empresa.get("cliente_id")

    # Obtener datos del formulario
    fecha_hora = request.form.get("fecha_hora")
    participantes = request.form.get("participantes")
    minuta = request.form.get("minuta")

    # Insertar reunión
    reunion_data = {
        "empresa_id": empresa_id,
        "cliente_id": cliente_id,
        "fecha_hora": fecha_hora,
        "participantes": participantes,
        "minuta": minuta,
        "creado_en": None  # que lo ponga la base de datos si hay default
    }
    supabase.table("reuniones_clientes").insert(reunion_data).execute()
    flash("✅ Reunión registrada correctamente", "success")
    return redirect(url_for("panel_cliente_clientes_bp.ficha_empresa", empresa_id=empresa_id))

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/accesos", methods=["GET", "POST"])
def editar_accesos_empresa(empresa_id):
    import uuid
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
        return redirect(url_for("login.login_screen"))

    # Obtener empresa
    empresa_resp = supabase.table("cliente_empresas").select("*").eq("id", empresa_id).single().execute()
    empresa = empresa_resp.data
    if not empresa:
        flash("❌ Empresa no encontrada", "error")
        return redirect(url_for("panel_cliente_clientes_bp.vista_empresas", nombre_nora=nombre_nora))

    if request.method == "POST":
        # Recibir listas de campos
        plataformas = request.form.getlist("acceso_plataforma")
        usuarios = request.form.getlist("acceso_usuario")
        contras = request.form.getlist("acceso_password")
        notas = request.form.getlist("acceso_notas")
        ids = request.form.getlist("acceso_id")

        # Leer accesos actuales en la base
        accesos_actuales = supabase.table("empresa_accesos").select("*").eq("empresa_id", empresa_id).execute().data or []
        ids_actuales = {str(a['id']): a for a in accesos_actuales if a.get('id')}
        ids_enviados = set([i for i in ids if i])

        # Actualizar o crear
        for idx, plataforma in enumerate(plataformas):
            if not plataforma.strip():
                continue
            acceso_data = {
                "empresa_id": empresa_id,
                "plataforma": plataforma.strip(),
                "usuario": usuarios[idx].strip() if idx < len(usuarios) else None,
                "password": contras[idx].strip() if idx < len(contras) else None,
                "notas": notas[idx].strip() if idx < len(notas) else None
            }
            acceso_id = ids[idx] if idx < len(ids) else None
            if acceso_id and acceso_id in ids_actuales:
                # Update
                supabase.table("empresa_accesos").update(acceso_data).eq("id", acceso_id).execute()
            else:
                # Insert
                acceso_data["id"] = str(uuid.uuid4())
                supabase.table("empresa_accesos").insert(acceso_data).execute()

        # Eliminar los que ya no están
        ids_a_eliminar = set(ids_actuales.keys()) - ids_enviados
        for del_id in ids_a_eliminar:
            supabase.table("empresa_accesos").delete().eq("id", del_id).execute()

        flash("✅ Accesos actualizados correctamente", "success")
        return redirect(url_for("panel_cliente_clientes_bp.ficha_empresa", empresa_id=empresa_id))

    # GET: mostrar accesos actuales
    accesos = supabase.table("empresa_accesos").select("*").eq("empresa_id", empresa_id).execute().data or []
    return render_template(
        "panel_cliente_empresa_accesos_form.html",
        empresa=empresa,
        accesos=accesos,
        nombre_nora=nombre_nora,
        user={"name": session.get("name", "Usuario")},
        modulo_activo="clientes"
    )

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/agregar_documento", methods=["POST"])
def agregar_documento(empresa_id):
    if not session.get("email"):
        return redirect(url_for("login.login_screen"))
    nombre = request.form.get("nombre", "").strip()
    url_doc = request.form.get("url", "").strip()
    if not nombre or not url_doc:
        flash("Nombre y URL son obligatorios", "error")
        return redirect(url_for("panel_cliente_clientes_bp.ficha_empresa", empresa_id=empresa_id))
    try:
        supabase.table("empresa_documentos").insert({
            "empresa_id": empresa_id,
            "nombre": nombre,
            "url": url_doc
        }).execute()
        flash("Documento agregado", "success")
    except Exception as e:
        flash(f"Error al agregar documento: {str(e)}", "error")
    return redirect(url_for("panel_cliente_clientes_bp.ficha_empresa", empresa_id=empresa_id))

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/eliminar_documento/<doc_id>", methods=["POST"])
def eliminar_documento(empresa_id, doc_id):
    if not session.get("email"):
        return redirect(url_for("login.login_screen"))
    try:
        supabase.table("empresa_documentos").delete().eq("id", doc_id).execute()
        flash("Documento eliminado", "success")
    except Exception as e:
        flash(f"Error al eliminar documento: {str(e)}", "error")
    return redirect(url_for("panel_cliente_clientes_bp.ficha_empresa", empresa_id=empresa_id))

@panel_cliente_clientes_bp.route("/empresa/<empresa_id>/ads/nueva", methods=["GET", "POST"])
def nueva_cuenta_ads_empresa(empresa_id):
    nombre_nora = request.path.split("/")[2]
    if not session.get("email"):
        return redirect(url_for('login.login_screen'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Validar empresa
    empresa = supabase.table("cliente_empresas").select("id,nombre_empresa").eq("id", empresa_id).single().execute().data
    if not empresa:
        return "Empresa no encontrada", 404

    if request.method == "POST":
        cuenta_data = {
            "id": str(uuid.uuid4()),
            "empresa_id": empresa_id,
            "nombre_nora": nombre_nora,
            "tipo_plataforma": request.form.get("tipo_plataforma"),
            "ad_account_id": request.form.get("ad_account_id"),
            "nombre_cuenta": request.form.get("nombre_cuenta"),
            "activo": True
        }
        supabase.table("meta_ads_cuentas").insert(cuenta_data).execute()
        flash("Cuenta publicitaria vinculada", "success")
        return redirect(url_for('panel_cliente_clientes_bp.vista_empresas', nombre_nora=nombre_nora))

    return render_template('panel_cliente_vincular_ads.html', nombre_nora=nombre_nora, empresa=empresa, user={"name": session.get("name", "Usuario")})
