print(">>> vista_presupuesto_nuevo.py importado")
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from supabase import create_client
import os
from clientes.aura.utils.login_required import login_required

panel_cliente_pagos_presupuesto_nuevo_bp = Blueprint("panel_cliente_pagos_presupuesto_nuevo", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_cliente_pagos_presupuesto_nuevo_bp.route("/<nombre_nora>/pagos/presupuestos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_presupuesto(nombre_nora):
    # Copia de vista_recibo_nuevo.py pero con formato='presupuesto' y sin estatus/forma_pago
    if request.method == "POST":
        try:
            print("POST recibido en presupuesto_nuevo")
            print("request.form:", request.form)
            # Procesar servicios seleccionados
            items = []
            ids      = request.form.getlist("servicio_id[]")
            print("ids:", ids)
            cant     = request.form.getlist("cantidad[]")
            print("cant:", cant)
            costos   = request.form.getlist("costo[]")
            print("costos:", costos)
            nombres  = request.form.getlist("nombre_servicio[]")
            print("nombres:", nombres)
            for i in range(len(cant)):
                print(f"Procesando item {i} - cant: {cant[i]}, costo: {costos[i]}, nombre: {nombres[i]}, id: {ids[i]}")
                if not cant[i]:
                    continue
                item = {
                    "servicio_id": ids[i] or None,
                    "nombre":      nombres[i] if nombres[i] else None,
                    "cantidad":    float(cant[i]),
                    "costo_unit":  float(costos[i]),
                }
                items.append(item)
            print("Items procesados:", items)
            total = sum(it["cantidad"] * it["costo_unit"] for it in items)
            print("Total calculado:", total)
            empresa_id = request.form["empresa_id"]
            print("empresa_id:", empresa_id)
            concepto = request.form["concepto"]
            print("concepto:", concepto)
            fecha_vencimiento = request.form["fecha_vencimiento"]
            print("fecha_vencimiento:", fecha_vencimiento)
            notas = request.form.get("notas") or ""
            print("notas:", notas)
            # Buscar cliente_id por empresa
            empresa_row = (
                supabase.table("cliente_empresas")
                    .select("cliente_id")
                    .eq("id", empresa_id)
                    .single()
                    .execute()
                    .data
            )
            print("empresa_row:", empresa_row)
            cliente_id = empresa_row["cliente_id"] if empresa_row and empresa_row.get("cliente_id") else None
            print("cliente_id:", cliente_id)
            if not cliente_id:
                print("No se pudo determinar el cliente para la empresa seleccionada.")
                flash("No se pudo determinar el cliente para la empresa seleccionada.", "error")
                return redirect(request.url)
            presupuesto_data = {
                "empresa_id": empresa_id,
                "cliente_id": cliente_id,
                "concepto": concepto,
                "monto": total,
                "fecha_vencimiento": fecha_vencimiento,
                "notas": notas,
                "nombre_nora": nombre_nora
            }
            print("Datos a guardar en presupuestos:", presupuesto_data)
            print("SUPABASE_URL usado:", SUPABASE_URL)
            print("SUPABASE_KEY usado:", SUPABASE_KEY)
            result = supabase.table("presupuestos").insert(presupuesto_data).execute()
            print("Resultado del insert en presupuestos:", result)
            print("Insert data:", getattr(result, 'data', None))
            print("Insert error:", getattr(result, 'error', None))
            if not result.data or not result.data[0].get("id"):
                print("Error al guardar presupuesto en presupuestos", result)
                flash("No se pudo guardar el presupuesto. Intenta de nuevo.", "error")
                return redirect(request.url)
            presupuesto_id = result.data[0]["id"]
            # Guardar ítems en presupuestos_items
            for it in items:
                print("Guardando item en presupuestos_items:", it)
                supabase.table("presupuestos_items").insert({
                    "presupuesto_id": presupuesto_id,
                    "servicio_id": it["servicio_id"],
                    "nombre":      it["nombre"],
                    "cantidad":    it["cantidad"],
                    "costo_unit":  it["costo_unit"],
                }).execute()
            print("Presupuesto guardado correctamente, id:", presupuesto_id)
            print("Antes del redirect final")
            return redirect(url_for("panel_cliente_pagos_presupuestos.panel_cliente_pagos_presupuestos", nombre_nora=nombre_nora))
        except Exception as e:
            print("EXCEPCION EN PRESUPUESTO NUEVO:", e)
            import traceback; traceback.print_exc()
            flash("Error inesperado: " + str(e), "error")
            return redirect(request.url)
    # Vista GET: igual que recibo_nuevo pero sin estatus/forma_pago
    empresas = (
        supabase.table("cliente_empresas")
            .select("id,nombre_empresa")
            .eq("nombre_nora", nombre_nora)
            .order("nombre_empresa")
            .execute()
            .data
    )
    # Servicios
    servicios_raw = (
        supabase.table("servicios")
            .select("id,titulo,costo,categoria")
            .eq("nombre_nora", nombre_nora)
            .execute()
            .data
    )
    servicios   = [
        {
            "id":        s["id"],
            "nombre":    s["titulo"],
            "costo":     s["costo"],
            "categoria": s.get("categoria") or "",
        }
        for s in servicios_raw
    ]
    categorias = sorted({s["categoria"] for s in servicios if s["categoria"]})
    return render_template(
        "panel_cliente_pagos/presupuesto_nuevo.html",
        empresas=empresas,
        servicios=servicios,
        categorias=categorias,
        nombre_nora=nombre_nora,
    )
