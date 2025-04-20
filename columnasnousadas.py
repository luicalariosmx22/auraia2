import os
import re
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

# === CONFIGURACIÓN ===
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
IGNORAR_COLUMNAS = {"id", "created_at", "updated_at"}  # <- Puedes agregar excepciones

class SupabaseTableChecker:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    def extraer_columnas_usadas(self, path_base: str) -> dict:
        usadas = {}
        for root, _, files in os.walk(path_base):
            for file in files:
                if not file.endswith(".py"):
                    continue
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    code = f.read()

                    # Buscar selects tipo .select("col1, col2, col3")
                    for match in re.findall(r'select\((.*?)\)', code):
                        columnas = re.findall(r'"(.*?)"|\'(.*?)\'', match)
                        for col in columnas:
                            col_name = col[0] or col[1]
                            if col_name == "*" or not col_name:
                                continue
                            for parte in col_name.split(","):
                                parte = parte.strip()
                                if "." in parte:
                                    tabla, campo = parte.split(".", 1)
                                    usadas.setdefault(tabla.strip(), set()).add(campo.strip())
                                else:
                                    usadas.setdefault("global", set()).add(parte.strip())

                    # Buscar condiciones tipo .eq("campo", valor)
                    for match in re.findall(r'\.(eq|ilike|like|contains|in_)\(["\'](\w+)["\']', code):
                        campo = match[1]
                        usadas.setdefault("global", set()).add(campo)
        return usadas

    def obtener_columnas_bd(self) -> dict:
        tablas_columnas = {}
        tablas = [
            "contactos", "historial_conversaciones", "logs_errores", "respuestas_bot",
            "categorias", "bot_data", "tickets", "configuracion_bot", "envios_programados",
            "etiquetas", "servicios_conocimiento"
        ]
        for tabla in tablas:
            try:
                res = self.supabase.table(tabla).select("*").limit(1).execute()
                if res.data:
                    columnas = list(res.data[0].keys())
                else:
                    columnas = [c for c in res.__dict__.get("_request", {}).get("query_params", {}).get("select", "").split(",") if c]
                tablas_columnas[tabla] = columnas
            except Exception as e:
                print(f"⚠️ No se pudo obtener columnas de '{tabla}': {str(e)}")
        return tablas_columnas

    def comparar_columnas(self, tablas_columnas: dict, columnas_usadas: dict) -> pd.DataFrame:
        resultados = []
        for tabla, columnas in tablas_columnas.items():
            usadas_en_tabla = columnas_usadas.get(tabla, set()) | columnas_usadas.get("global", set())
            no_usadas = [col for col in columnas if col not in usadas_en_tabla and col not in IGNORAR_COLUMNAS]
            for col in no_usadas:
                resultados.append({"tabla": tabla, "columna_no_usada": col})
        return pd.DataFrame(resultados)

    def generar_reporte(self, repo_path: str):
        print("🔍 Analizando columnas usadas en código...")
        columnas_usadas = self.extraer_columnas_usadas(repo_path)

        print("📦 Obteniendo columnas desde Supabase...")
        columnas_bd = self.obtener_columnas_bd()

        print("📊 Comparando...")
        df_resultado = self.comparar_columnas(columnas_bd, columnas_usadas)

        if df_resultado.empty:
            print("✅ No se encontraron columnas sin uso.")
        else:
            print("❌ Columnas que existen pero no se usan:")
            print(df_resultado)
            df_resultado.to_csv("columnas_no_usadas.csv", index=False)
            print("\n📝 Guardado en columnas_no_usadas.csv")

if __name__ == "__main__":
    REPO_PATH = "https://github.com/luicalariosmx22/auraia2/tree/master/clientes/aura/routes"  # <- Ajusta si tu código está en otra carpeta
    checker = SupabaseTableChecker()
    checker.generar_reporte(REPO_PATH)
