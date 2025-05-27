import random
import string
from datetime import datetime

from clientes.aura.utils.supabase_client import supabase


def generar_codigo_tarea(iniciales):
    """
    Devuelve un código único con formato <INICIALES>-YYMMDD-XXXX.
    • iniciales: lista o string con las palabras del nombre del usuario (se usan sus primeras letras).
    """
    # Normalizar a lista
    if isinstance(iniciales, str):
        iniciales = iniciales.split()

    # Prefijo de hasta 2 letras
    prefijo = "".join(palabra[:1] for palabra in iniciales).upper()[:2] or "TR"
    fecha = datetime.utcnow().strftime("%y%m%d")

    while True:
        sufijo = "".join(random.choices(string.digits, k=4))
        codigo = f"{prefijo}-{fecha}-{sufijo}"

        # Verificar que no exista ya en la tabla tareas
        try:
            existe = (
                supabase.table("tareas")
                .select("id")
                .eq("codigo_tarea", codigo)
                .limit(1)
                .execute()
            )
            if not existe.data:
                return codigo
        except Exception:
            # Si falla la verificación, devolver de todos modos para no bloquear la creación
            return codigo
