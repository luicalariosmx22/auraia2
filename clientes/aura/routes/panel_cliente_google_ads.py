from flask import Blueprint, render_template, current_app

panel_cliente_google_ads_bp = Blueprint(
    "panel_cliente_google_ads_bp",
    __name__,
    template_folder="../../templates"
)

@panel_cliente_google_ads_bp.route("/panel_cliente/<nombre_nora>/google_ads/")
def panel_cliente_google_ads(nombre_nora):
    try:
        current_app.logger.info(f"[Google Ads] Entrando a la vista Google Ads para {nombre_nora}")
        return render_template("panel_cliente_google_ads.html", nombre_nora=nombre_nora)
    except Exception as e:
        current_app.logger.error(f"[Google Ads] Error en index: {e}", exc_info=True)
        return f"Error en Google Ads: {e}", 500

# El archivo panel_cliente_google_ads.py ya no es necesario tras la migración del módulo Google Ads.
