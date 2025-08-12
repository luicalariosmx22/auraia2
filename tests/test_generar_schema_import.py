#!/usr/bin/env python3
"""
🔧 TEST: Verificar que generar_supabase_schema.py no falla
"""

import os
import sys

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("🔍 Probando import de generar_supabase_schema.py...")

try:
    from clientes.aura.scripts.generar_supabase_schema import HAS_PSICOPG2
    print(f"✅ Import exitoso - psicopg2 disponible: {HAS_PSICOPG2}")
    print("✅ El script ya no falla por psicopg2")
except Exception as e:
    print(f"❌ Error en import: {e}")
    sys.exit(1)

print("🎉 Script corregido exitosamente")
