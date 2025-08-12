"""
Script para agregar el módulo de agenda al sistema de registro dinámico
Este código debe agregarse a clientes/aura/registro/registro_dinamico.py
"""

def agregar_agenda_a_registro_dinamico():
    """
    Código que debe agregarse en clientes/aura/registro/registro_dinamico.py
    dentro de la función registrar_modulos_dinamicos()
    """
    
    codigo_agenda = '''
        # Módulo de Agenda - Gestión de eventos y Google Calendar
        if "agenda" in modulos:
            try:
                from clientes.aura.routes.panel_cliente_agenda import panel_cliente_agenda_bp
                safe_register_blueprint(app, panel_cliente_agenda_bp)
                print(f"✅ Módulo de agenda registrado para {nombre_nora}")
                
            except ImportError as e:
                print(f"❌ Error importando módulo agenda: {e}")
            except Exception as e:
                print(f"❌ Error registrando módulo agenda: {e}")
    '''
    
    return codigo_agenda

def mostrar_instrucciones():
    """Muestra las instrucciones para integrar el módulo"""
    print("📋 INSTRUCCIONES PARA INTEGRAR MÓDULO AGENDA")
    print("=" * 60)
    
    print("\n1. 🗂️ Ubicar archivo:")
    print("   clientes/aura/registro/registro_dinamico.py")
    
    print("\n2. 🔍 Buscar la función:")
    print("   def registrar_modulos_dinamicos(app, nombre_nora=None):")
    
    print("\n3. 📝 Agregar este código DESPUÉS de los otros módulos:")
    codigo = agregar_agenda_a_registro_dinamico()
    print(codigo)
    
    print("\n4. 💾 Guardar el archivo")
    
    print("\n5. 🔄 Reiniciar el servidor:")
    print("   python dev_start.py")
    
    print("\n6. 🌐 Acceder al módulo:")
    print("   http://localhost:5000/panel_cliente/aura/agenda/")
    
    print("\n" + "=" * 60)
    print("✅ Una vez agregado, el módulo estará disponible automáticamente")

if __name__ == "__main__":
    mostrar_instrucciones()
