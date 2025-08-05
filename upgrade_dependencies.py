"""
Script para actualizar las dependencias de AuraAi2 a versiones compatibles.

Este script actualiza Flask, Werkzeug y Flask-Session a versiones específicas
que son conocidas por funcionar correctamente juntas y evitar problemas con
las cookies de sesión.
"""
import subprocess
import sys
import os
import re

def update_requirements_file():
    """
    Actualiza el archivo requirements.txt con las versiones específicas necesarias
    para resolver el problema de cookies de sesión.
    """
    # Paquetes a actualizar con versiones específicas
    packages = {
        "werkzeug": "2.0.3",
        "flask": "2.0.3",
        "flask-session": "0.4.0",
        "itsdangerous": "2.0.1",
        "jinja2": "3.0.3",
        "markupsafe": "2.0.1"
    }
    
    # Ruta al archivo requirements.txt
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(req_path):
        print(f"⚠️ No se encontró el archivo requirements.txt en {req_path}")
        create_new = input("¿Crear un nuevo archivo requirements.txt? (s/n): ").lower() == 's'
        if create_new:
            with open(req_path, 'w', encoding='utf-8') as f:
                for package, version in packages.items():
                    f.write(f"{package}=={version}\n")
            print(f"✅ Se ha creado un nuevo archivo requirements.txt con las versiones compatibles")
            return True
        else:
            return False
    
    # Leer el archivo actual
    with open(req_path, 'r', encoding='utf-8') as f:
        requirements = f.readlines()
    
    # Crear un respaldo del archivo original
    backup_path = req_path + '.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(requirements)
    print(f"✅ Respaldo creado en {backup_path}")
    
    # Actualizar las versiones de los paquetes
    updated_requirements = []
    updated_packages = set()
    
    for line in requirements:
        line = line.strip()
        if not line or line.startswith('#'):
            updated_requirements.append(line + '\n')
            continue
        
        # Buscar coincidencias de paquetes (ignorando versiones existentes)
        match = re.match(r'^([a-zA-Z0-9_\-]+).*', line)
        if match:
            package_name = match.group(1).lower()
            # Comprobar si este paquete está en nuestra lista de actualizaciones
            for target_pkg in packages:
                if package_name == target_pkg.lower():
                    updated_requirements.append(f"{target_pkg}=={packages[target_pkg]}\n")
                    updated_packages.add(target_pkg)
                    print(f"📝 Actualizado {package_name} a la versión {packages[target_pkg]}")
                    break
            else:
                # Si no está en la lista de actualizaciones, mantener la línea original
                updated_requirements.append(line + '\n')
        else:
            updated_requirements.append(line + '\n')
    
    # Agregar paquetes que no estaban en el archivo original
    for package, version in packages.items():
        if package not in updated_packages:
            updated_requirements.append(f"{package}=={version}\n")
            print(f"➕ Agregado {package}=={version} al archivo requirements.txt")
    
    # Escribir el archivo actualizado
    with open(req_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_requirements)
    
    print(f"✅ Archivo requirements.txt actualizado correctamente")
    return True

def install_from_requirements():
    """
    Instala los paquetes desde el archivo requirements.txt
    """
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    try:
        print("🔄 Instalando dependencias desde requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def main():
    """
    Actualiza las dependencias a versiones compatibles.
    """
    print("🔄 Iniciando actualización de dependencias compatibles...")
    
    # Verificar entorno virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ No se detectó un entorno virtual activo.")
        use_venv = input("¿Deseas continuar de todos modos? (s/n): ").lower() == 's'
        if not use_venv:
            print("❌ Operación cancelada.")
            return
    
    # Actualizar el archivo requirements.txt
    if update_requirements_file():
        # Preguntar si quiere instalar las dependencias ahora
        install_now = input("¿Quieres instalar las dependencias actualizadas ahora? (s/n): ").lower() == 's'
        if install_now:
            install_from_requirements()
        else:
            print("\n⚠️ Recuerda instalar las dependencias con: pip install -r requirements.txt")
    else:
        print("❌ No se pudo actualizar el archivo requirements.txt")
    
    print("\n⚠️ Recuerda reiniciar tu servidor Flask después de actualizar las dependencias.")

if __name__ == "__main__":
    main()