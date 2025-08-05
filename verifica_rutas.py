# Script para ejecutar el verificador de rutas en tiempo de ejecución
from clientes.aura import create_app
from clientes.aura.utils.verificador_rutas_runtime import verificar_rutas_vs_html

if __name__ == "__main__":
    app, *_ = create_app()  # Desempaqueta solo la instancia Flask
    rutas_faltantes = verificar_rutas_vs_html(app)
    print("\nRutas usadas en HTML que NO existen en Flask:")
    for ruta in rutas_faltantes:
        print(ruta)
    if not rutas_faltantes:
        print("\n✅ Todas las rutas usadas en los HTML existen en Flask.")
