# --- Forzar rutas robustas con Path ---
from pathlib import Path
import ast
import re
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def verificar_uso_variables_en_templates(modulo):
    print("\n🔍 Verificación cruzada: variables pasadas en render_template vs uso en HTML")

    archivo_py = ROOT_DIR / f"clientes/aura/routes/panel_cliente_{modulo}/panel_cliente_{modulo}.py"
    carpeta_templates = ROOT_DIR / f"clientes/aura/templates/panel_cliente_{modulo}"

    if not archivo_py.exists() or not carpeta_templates.exists():
        print("❌ No se encontró archivo .py o carpeta de templates.")
        return

    contenido = archivo_py.read_text(encoding="utf-8")

    # 🧠 Detectar llamadas a render_template(...)
    bloques = re.findall(r'render_template\((.*?)\)', contenido, re.DOTALL)
    todas_variables = set()
    for bloque in bloques:
        variables = re.findall(r'(\w+)\s*=', bloque)
        todas_variables.update(variables)

    if not todas_variables:
        print("⚠️ No se detectaron variables pasadas en render_template.")
        return

    print(f"📤 Variables detectadas: {', '.join(sorted(todas_variables))}")

    # 📂 Buscar si aparecen en HTML
    no_encontradas = set(todas_variables)
    for template in carpeta_templates.glob("*.html"):
        contenido_html = template.read_text(encoding="utf-8")
        for var in todas_variables:
            if f"{{{{ {var} " in contenido_html or f"{{{{ {var}}}" in contenido_html or f"{var}." in contenido_html:
                no_encontradas.discard(var)
                print(f"✅ {{ {{ {var} }} }} detectado en {template.name}")

    if no_encontradas:
        print("\n⚠️ Variables pasadas a render_template pero no usadas en templates:")
        for var in no_encontradas:
            print(f"   ❌ {var}")

    else:
        print("✅ Todas las variables se usan en los templates.")
