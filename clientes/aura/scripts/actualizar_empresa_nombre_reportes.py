from clientes.aura.utils.supabase_client import supabase

def actualizar_empresa_nombre_en_reportes():
    # 1️⃣ Traemos todos los reportes donde falte empresa_nombre (solo los nulos o vacíos)
    reportes = supabase.table('meta_ads_reportes_semanales') \
        .select('id, id_cuenta_publicitaria, empresa_id') \
        .or_('empresa_nombre.is.null(),empresa_nombre.eq.("")') \
        .limit(1000).execute().data or []

    print(f"🔎 Reportes a actualizar: {len(reportes)}")
    actualizados = 0

    for reporte in reportes:
        cuenta_id = reporte.get('id_cuenta_publicitaria')
        if not cuenta_id:
            continue

        # Buscar el nombre de la empresa desde meta_ads_cuentas (usando nombre_cliente)
        cuenta = supabase.table('meta_ads_cuentas') \
            .select('nombre_cliente') \
            .eq('id_cuenta_publicitaria', cuenta_id) \
            .single().execute().data

        if cuenta and cuenta.get('nombre_cliente'):
            supabase.table('meta_ads_reportes_semanales') \
                .update({'empresa_nombre': cuenta['nombre_cliente']}) \
                .eq('id', reporte['id']).execute()
            print(f"✅ Actualizado reporte ID {reporte['id']} con empresa {cuenta['nombre_cliente']}")
            actualizados += 1

    print(f"🎯 Total actualizados: {actualizados}")

# Si quieres ejecutarlo directamente:
if __name__ == "__main__":
    actualizar_empresa_nombre_en_reportes()

# Registro del blueprint si se ejecuta como script
try:
    from flask import Flask
    from clientes.aura.routes.panel_cliente_meta_ads.estadisticas import estadisticas_ads_bp
    app = Flask(__name__)
    app.register_blueprint(estadisticas_ads_bp)
    print("Blueprint 'estadisticas_ads_bp' registrado para pruebas.")
except Exception as e:
    print(f"[WARN] No se pudo registrar el blueprint: {e}")
