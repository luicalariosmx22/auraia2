#!/usr/bin/env python3
"""
🧪 Test rápido para verificar David Alcantara
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.auth.google_login import es_administrador_google

# Simular datos de David Alcantara según la estructura real
usuario_david = {
    'rol': 'interno',
    'es_supervisor': False,
    'es_supervisor_tareas': False,
    'modulos': ['tareas']
}

print('🧪 Test con datos reales de David Alcantara:')
es_admin = es_administrador_google(usuario_david)
print(f'Rol: {usuario_david["rol"]}')
print(f'Módulos: {usuario_david["modulos"]}')
print(f'Es admin: {es_admin}')

if es_admin:
    print('✅ David sería reconocido como ADMINISTRADOR')
else:
    print('❌ David NO sería reconocido como administrador')

# Test adicional con el email real
print('\n🔍 Test de verificación de usuario:')
from clientes.aura.auth.google_login import verificar_usuario_google

usuario_real = verificar_usuario_google("guitarrasdavidalcantara@gmail.com")
if usuario_real:
    es_admin_real = es_administrador_google(usuario_real)
    print(f'✅ Usuario encontrado: {usuario_real["nombre"]}')
    print(f'📊 Es admin (datos reales): {es_admin_real}')
else:
    print('❌ Usuario no encontrado')
