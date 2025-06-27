#!/usr/bin/env python3
"""
Google Ads Excel to SQL Generator
Convertidor de archivos Excel de Google Ads a sentencias SQL para Supabase
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def show_menu():
    """Muestra el menú principal"""
    print("🎯 GOOGLE ADS EXCEL TO SQL GENERATOR")
    print("=" * 50)
    print("📊 Convierte archivos Excel de Google Ads a SQL para Supabase")
    print()
    print("OPCIONES DISPONIBLES:")
    print("1. 🤖 Generador con IA (OpenAI) - Mapeo automático inteligente")
    print("2. ⚡ Generador simple - Mapeo predefinido rápido")  
    print("3. 🧪 Ejecutar tests con datos de ejemplo")
    print("4. 📚 Ver documentación")
    print("5. ❌ Salir")
    print()

def run_ai_generator():
    """Ejecuta el generador con IA"""
    print("\n🤖 INICIANDO GENERADOR CON IA")
    print("=" * 40)
    
    # Verificar API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: No se encontró OPENAI_API_KEY")
        print("📝 Instrucciones:")
        print("   1. Edita el archivo .env")
        print("   2. Agrega: OPENAI_API_KEY=tu_api_key_aqui")
        print("   3. Guarda el archivo y ejecuta de nuevo")
        return
    
    try:
        from google_ads_sql_generator import GoogleAdsExcelAnalyzer
        
        analyzer = GoogleAdsExcelAnalyzer()
        
        # Solicitar datos del usuario
        print("\n📋 CONFIGURACIÓN:")
        excel_file = input("📁 Ruta del archivo Excel: ").strip().strip('"')
        
        if not os.path.exists(excel_file):
            print(f"❌ Error: Archivo no encontrado: {excel_file}")
            return
        
        sheet_name = input("📄 Nombre de la hoja (Enter para la primera): ").strip()
        if not sheet_name:
            sheet_name = None
        
        output_file = input("💾 Archivo SQL de salida (Enter para 'google_ads_ai.sql'): ").strip()
        if not output_file:
            output_file = "google_ads_ai.sql"
        
        # Procesar
        result = analyzer.process_excel_to_sql(excel_file, output_file, sheet_name)
        
        if result['success']:
            print(f"\n🎉 ¡ÉXITO! Archivo generado: {result['output_file']}")
            print(f"📊 Total de registros: {result['total_records']}")
            print("\n📋 SIGUIENTES PASOS:")
            print("1. Revisa el archivo SQL generado")
            print("2. Ejecuta las sentencias en Supabase")
            print("3. Verifica los datos insertados")
        else:
            print(f"\n💥 ERROR: {result['error']}")
    
    except ImportError:
        print("❌ Error: No se pudieron importar las dependencias necesarias")
        print("💡 Ejecuta: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

def run_simple_generator():
    """Ejecuta el generador simple"""
    print("\n⚡ INICIANDO GENERADOR SIMPLE")
    print("=" * 40)
    
    try:
        from simple_excel_to_sql import SimpleExcelToSQL
        
        converter = SimpleExcelToSQL()
        
        # Solicitar datos del usuario
        print("\n📋 CONFIGURACIÓN:")
        excel_file = input("📁 Ruta del archivo Excel: ").strip().strip('"')
        
        if not os.path.exists(excel_file):
            print(f"❌ Error: Archivo no encontrado: {excel_file}")
            return
        
        output_file = input("💾 Archivo SQL de salida (Enter para 'google_ads_simple.sql'): ").strip()
        if not output_file:
            output_file = "google_ads_simple.sql"
        
        # Procesar
        success = converter.process_excel_simple(excel_file, output_file)
        
        if success:
            print(f"\n🎉 ¡ÉXITO! Archivo generado: {output_file}")
            print("\n📋 SIGUIENTES PASOS:")
            print("1. Revisa el archivo SQL generado")
            print("2. Ejecuta las sentencias en Supabase") 
            print("3. Verifica los datos insertados")
        else:
            print("\n💥 ERROR durante el proceso")
    
    except ImportError:
        print("❌ Error: No se pudieron importar las dependencias necesarias")
        print("💡 Ejecuta: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

def run_tests():
    """Ejecuta los tests"""
    print("\n🧪 EJECUTANDO SUITE DE PRUEBAS")
    print("=" * 40)
    
    try:
        from test_generators import main as test_main
        test_main()
    except ImportError:
        print("❌ Error: No se pudieron importar los módulos de test")
    except Exception as e:
        print(f"❌ Error en tests: {str(e)}")

def show_documentation():
    """Muestra la documentación"""
    print("\n📚 DOCUMENTACIÓN")
    print("=" * 40)
    
    docs = """
🎯 PROPÓSITO:
Convierte archivos Excel de reportes de Google Ads en sentencias SQL INSERT
para la tabla google_ads_reporte_anuncios en Supabase.

📊 TABLA DESTINO:
- 65 columnas que incluyen títulos, descripciones, métricas y configuración
- Soporta hasta 15 títulos y 4 descripciones por anuncio
- Métricas: clics, impresiones, CTR, CPC, conversiones, etc.

🤖 GENERADOR CON IA:
- Usa OpenAI GPT-4 para mapeo automático
- Analiza estructura del Excel inteligentemente  
- Mejor para archivos con columnas no estándar
- Requiere OPENAI_API_KEY

⚡ GENERADOR SIMPLE:
- Mapeo predefinido para columnas comunes de Google Ads
- No requiere API externa
- Más rápido para archivos estándar
- Ideal para reportes regulares

📁 ARCHIVOS:
- google_ads_sql_generator.py (principal con IA)
- simple_excel_to_sql.py (alternativo simple)
- test_generators.py (pruebas)
- requirements.txt (dependencias)
- .env (configuración)

🔧 CONFIGURACIÓN:
1. pip install -r requirements.txt
2. Configurar OPENAI_API_KEY en .env (solo para IA)
3. Ejecutar main.py y seguir menú

📝 FORMATO DE SALIDA:
Archivo .sql con sentencias INSERT listas para ejecutar en Supabase.
"""
    print(docs)

def main():
    """Función principal"""
    while True:
        show_menu()
        
        try:
            choice = input("🔥 Selecciona una opción (1-5): ").strip()
            
            if choice == '1':
                run_ai_generator()
            elif choice == '2':
                run_simple_generator()
            elif choice == '3':
                run_tests()
            elif choice == '4':
                show_documentation()
            elif choice == '5':
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("\n❌ Opción inválida. Por favor selecciona 1-5.")
            
            input("\n⏸️ Presiona Enter para continuar...")
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            input("\n⏸️ Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
