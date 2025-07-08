# ✅ Archivo: clientes/aura/routes/debug/verificar_keywords.py
# 👉 Vista para detectar argumentos duplicados o SyntaxErrors

from flask import Blueprint, render_template
import ast
import os

verificar_keywords_bp = Blueprint("debug_keywords", __name__, url_prefix="/debug")

def check_keywords_in_file(file_path):
    errores = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except SyntaxError as e:
        errores.append({
            "archivo": file_path,
            "linea": e.lineno,
            "error": f"❌ SyntaxError: {e.msg}"
        })
        return errores

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seen = set()
            for kw in node.keywords:
                if kw.arg in seen:
                    errores.append({
                        "archivo": file_path,
                        "linea": kw.lineno,
                        "error": f"❌ Argumento duplicado: '{kw.arg}'"
                    })
                seen.add(kw.arg)
    return errores

@verificar_keywords_bp.route("/verificar_keywords")
def verificar_keywords():
    base_folder = "clientes"
    errores = []

    for dirpath, _, filenames in os.walk(base_folder):
        for filename in filenames:
            if filename.endswith(".py"):
                ruta = os.path.join(dirpath, filename)
                errores.extend(check_keywords_in_file(ruta))

    return render_template("debug/verificar_keywords.html", errores=errores)
