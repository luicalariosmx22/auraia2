import webview
import os
from columnasnousadas import SupabaseTableChecker
from typing import List

class Api:
    def seleccionar_ruta(self):
        import tkinter as tk
        from tkinter import filedialog
        try:
            root = tk.Tk()
            root.withdraw()
            ruta = filedialog.askdirectory()

            if ruta:
                checker = SupabaseTableChecker()

                print("🔍 Analizando columnas usadas en código...")
                columnas_usadas = checker.extraer_columnas_usadas(ruta)

                print("📦 Obteniendo columnas desde Supabase...")
                columnas_bd = checker.obtener_columnas_bd()

                print("📊 Comparando columnas no usadas...")
                df_no_usadas = checker.comparar_columnas(columnas_bd, columnas_usadas)

                print("📊 Verificando columnas que no están en la base de datos...")
                columnas_faltantes = self.verificar_columnas_faltantes(columnas_usadas, columnas_bd)

                reporte = ""

                if df_no_usadas.empty:
                    reporte += "✅ No se encontraron columnas sin uso.\n"
                else:
                    reporte += "❌ Columnas que existen pero no se usan:\n"
                    reporte += df_no_usadas.to_string(index=False)
                    df_no_usadas.to_csv("columnas_no_usadas.csv", index=False)
                    reporte += "\n\n📝 Guardado en columnas_no_usadas.csv\n"

                if not columnas_faltantes:
                    reporte += "✅ Todas las columnas usadas están en la base de datos.\n"
                else:
                    reporte += "❌ Columnas usadas en el código pero no encontradas en la base de datos:\n"
                    reporte += "\n".join(columnas_faltantes)
                    with open("columnas_faltantes.txt", "w", encoding="utf-8") as f:
                        f.write("\n".join(columnas_faltantes))
                    reporte += "\n\n📝 Guardado en columnas_faltantes.txt\n"

                return {"ruta": ruta, "reporte": reporte}
            return {"ruta": "Sin seleccionar", "reporte": "⚠️ No se generó ningún reporte."}
        except Exception as e:
            return {"ruta": "Error", "reporte": f"⚠️ Error al generar el reporte: {str(e)}"}

    def verificar_columnas_faltantes(self, columnas_usadas: dict, columnas_bd: dict) -> List[str]:
        """Verifica las columnas usadas en el código que no están en la base de datos"""
        faltantes = []
        for tabla, columnas in columnas_usadas.items():
            if tabla not in columnas_bd:
                faltantes.append(f"Tabla '{tabla}' no encontrada en la base de datos.")
                continue

            columnas_bd_tabla = set(columnas_bd[tabla])
            for columna in columnas:
                if columna not in columnas_bd_tabla:
                    faltantes.append(f"Columna '{columna}' en tabla '{tabla}' no encontrada en la base de datos.")
        return faltantes

if __name__ == '__main__':
    html_file = "verificador.html"
    if not os.path.exists(html_file):
        print(f"⚠️ Error: No se encontró el archivo {html_file}")
    else:
        api = Api()
        ventana = webview.create_window(
            "Verificador Supabase",
            html_file,
            js_api=api,
            width=900,
            height=700
        )
        webview.start()
