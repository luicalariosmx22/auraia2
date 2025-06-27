#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Test de Permisos de Administrador
"""

from clientes.aura.auth.google_login import es_administrador_google

def test_permisos_david():
    """Test con datos reales de David Alcantara"""
    print("🧪 Test con datos reales de David Alcantara:")
    
    usuario_david = {
        'rol': 'interno',
        'es_supervisor': False,
        'es_supervisor_tareas': False,
        'modulos': ['tareas']
    }
    
    es_admin = es_administrador_google(usuario_david)
    print(f"Rol: {usuario_david['rol']}")
    print(f"Módulos: {usuario_david['modulos']}")
    print(f"Es admin: {es_admin}")
    
    if es_admin:
        print("✅ David sería reconocido como ADMINISTRADOR")
        return True
    else:
        print("❌ David NO sería reconocido como administrador")
        return False

def test_otros_casos():
    """Test con otros casos"""
    print("\n🧪 Test con otros casos:")
    
    casos = [
        {"rol": "admin", "resultado_esperado": True},
        {"rol": "cliente", "es_supervisor": True, "resultado_esperado": True},
        {"rol": "usuario", "es_supervisor_tareas": True, "resultado_esperado": True},
        {"rol": "cliente", "resultado_esperado": False},
    ]
    
    for i, caso in enumerate(casos, 1):
        resultado = es_administrador_google(caso)
        esperado = caso.pop("resultado_esperado")
        estado = "✅" if resultado == esperado else "❌"
        print(f"{estado} Caso {i}: {caso} -> Admin: {resultado}")

if __name__ == "__main__":
    print("🚀 Iniciando tests de permisos de administrador...")
    test_permisos_david()
    test_otros_casos()
    print("🏁 Tests completados")
