from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from clientes.aura.utils.supabase_client import supabase

login_cambiar_password_bp = Blueprint("cambiar_password", __name__)

@login_cambiar_password_bp.route("/cambiar_contrasena", methods=["GET", "POST"])
def cambiar_contrasena():
    if request.method == "GET":
        return render_template("cambiar_contrasena.html")

    correo = request.form.get("correo")
    actual = request.form.get("actual")
    nueva = request.form.get("nueva")
    confirmar = request.form.get("confirmar")

    print("📩 Cambio solicitado por:", correo)

    if not correo or not actual or not nueva or not confirmar:
        flash("❌ Todos los campos son obligatorios")
        return redirect(url_for("cambiar_password.cambiar_contrasena"))

    if actual != "123Aura!":
        flash("❌ La contraseña actual es incorrecta")
        return redirect(url_for("cambiar_password.cambiar_contrasena"))

    if nueva != confirmar:
        flash("❌ Las nuevas contraseñas no coinciden")
        return redirect(url_for("cambiar_password.cambiar_contrasena"))

    print("🔍 Buscando en super_admins...")
    admin = supabase.table("super_admins").select("id").eq("correo", correo).eq("activo", True).execute()
    if admin.data:
        supabase.table("super_admins").update({"password": nueva}).eq("correo", correo).execute()
        print("✅ Contraseña cambiada para admin")
        flash("✅ Contraseña actualizada correctamente (Admin)")
        return redirect("/login")

    print("🔍 Buscando en usuarios_clientes...")
    user = supabase.table("usuarios_clientes").select("id").eq("correo", correo).execute()
    if user.data:
        supabase.table("usuarios_clientes").update({"password": nueva}).eq("correo", correo).execute()
        print("✅ Contraseña cambiada para usuario cliente")
        flash("✅ Contraseña actualizada correctamente (Usuario)")
        return redirect("/login")

    print("❌ No se encontró una cuenta con ese correo")
    flash("❌ No se encontró una cuenta asociada a ese correo")
    return redirect(url_for("cambiar_password.cambiar_contrasena"))
