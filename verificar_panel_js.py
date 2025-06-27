#!/usr/bin/env python3
"""
🧪 Script de prueba rápida para verificar la configuración del panel de entrenamiento
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_archivos_js():
    """Verificar que todos los archivos JavaScript existan"""
    archivos_js = [
        'clientes/aura/static/js/panel-entrenamiento-core.js',
        'clientes/aura/static/js/ui-utils.js',
        'clientes/aura/static/js/conocimiento-manager.js',
        'clientes/aura/static/js/form-handlers.js'
    ]
    
    print("🔍 Verificando archivos JavaScript...")
    for archivo in archivos_js:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
            # Verificar contenido básico
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if 'function' in contenido:
                    print(f"   📋 Contiene funciones")
                else:
                    print(f"   ⚠️ No parece contener funciones")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
    
    print()

def verificar_template():
    """Verificar el template"""
    template_path = 'clientes/aura/templates/admin_nora_entrenar.html'
    
    print("🔍 Verificando template...")
    if os.path.exists(template_path):
        print(f"✅ {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Verificar referencias a archivos JS
        archivos_referenciados = [
            'panel-entrenamiento-core.js',
            'ui-utils.js',
            'conocimiento-manager.js',
            'form-handlers.js'
        ]
        
        for archivo in archivos_referenciados:
            if archivo in contenido:
                print(f"   ✅ Referencia a {archivo}")
            else:
                print(f"   ❌ NO referencia a {archivo}")
        
        # Verificar configuración
        if 'PANEL_CONFIG' in contenido:
            print("   ✅ Configuración PANEL_CONFIG presente")
        else:
            print("   ❌ Configuración PANEL_CONFIG ausente")
            
    else:
        print(f"❌ {template_path} - NO ENCONTRADO")
    
    print()

def generar_html_prueba():
    """Generar archivo HTML de prueba independiente"""
    html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧪 Prueba Panel Entrenamiento</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">🧪 Prueba Panel Entrenamiento</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Pruebas de Navegación</h2>
                <div class="space-y-2">
                    <button onclick="testScrollToSection()" class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Test scrollToSection()
                    </button>
                    <button onclick="testToggleExamples()" class="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                        Test toggleExamples()
                    </button>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Pruebas de Configuración</h2>
                <div class="space-y-2">
                    <button onclick="testPanelConfig()" class="w-full bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                        Test PANEL_CONFIG
                    </button>
                    <button onclick="testFunctions()" class="w-full bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600">
                        Test Todas las Funciones
                    </button>
                </div>
            </div>
        </div>
        
        <div id="test-section" class="bg-yellow-100 p-4 rounded-lg mb-6">
            <h3 class="font-semibold">🎯 Sección de Prueba para Scroll</h3>
            <p>Esta sección se usa para probar la función scrollToSection().</p>
        </div>
        
        <div id="examples-container" class="hidden bg-green-100 p-4 rounded-lg mb-6">
            <h3 class="font-semibold">📝 Ejemplos Container</h3>
            <p>Este container se muestra/oculta con toggleExamples().</p>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="font-semibold mb-2">📊 Output de Pruebas:</h3>
            <pre id="output-content" class="text-sm bg-black text-green-400 p-3 rounded max-h-64 overflow-auto"></pre>
        </div>
    </div>
    
    <!-- Scripts en orden correcto -->
    <script src="clientes/aura/static/js/panel-entrenamiento-core.js"></script>
    <script src="clientes/aura/static/js/ui-utils.js"></script>
    <script src="clientes/aura/static/js/conocimiento-manager.js"></script>
    <script src="clientes/aura/static/js/form-handlers.js"></script>
    
    <script>
    // Simular configuración del template
    if (typeof PANEL_CONFIG !== 'undefined') {
        PANEL_CONFIG.nombreNora = 'test-nora';
        PANEL_CONFIG.endpoints = {
            bloques: '/panel_cliente/test-nora/entrenar/bloques',
            personalidad: '/panel_cliente/test-nora/entrenar/personalidad',
            instrucciones: '/panel_cliente/test-nora/entrenar/instrucciones',
            estadoIA: '/panel_cliente/test-nora/entrenar/estado_ia',
            limites: '/panel_cliente/test-nora/entrenar/limites',
            bienvenida: '/panel_cliente/test-nora/entrenar/bienvenida'
        };
    }
    
    function log(message, type = 'info') {
        const output = document.getElementById('output-content');
        const timestamp = new Date().toLocaleTimeString();
        const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️';
        output.textContent += `${timestamp} ${icon} ${message}\\n`;
        output.scrollTop = output.scrollHeight;
    }
    
    function testScrollToSection() {
        log('Probando scrollToSection...');
        if (typeof scrollToSection === 'function') {
            try {
                scrollToSection('test-section');
                log('scrollToSection ejecutada correctamente', 'success');
            } catch (e) {
                log('Error en scrollToSection: ' + e.message, 'error');
            }
        } else {
            log('scrollToSection no está definida', 'error');
        }
    }
    
    function testToggleExamples() {
        log('Probando toggleExamples...');
        if (typeof toggleExamples === 'function') {
            try {
                toggleExamples();
                log('toggleExamples ejecutada correctamente', 'success');
            } catch (e) {
                log('Error en toggleExamples: ' + e.message, 'error');
            }
        } else {
            log('toggleExamples no está definida', 'error');
        }
    }
    
    function testPanelConfig() {
        log('Probando PANEL_CONFIG...');
        if (typeof PANEL_CONFIG !== 'undefined') {
            log('PANEL_CONFIG definido correctamente', 'success');
            log('nombreNora: ' + PANEL_CONFIG.nombreNora);
            log('endpoints: ' + Object.keys(PANEL_CONFIG.endpoints).length + ' endpoints');
        } else {
            log('PANEL_CONFIG no está definido', 'error');
        }
    }
    
    function testFunctions() {
        log('=== INICIANDO PRUEBA COMPLETA ===');
        
        const funciones = [
            'scrollToSection',
            'toggleExamples',
            'initializeTabs',
            'initializeFormHandlers',
            'initializeCharacterCounters',
            'cargarConocimiento'
        ];
        
        funciones.forEach(fn => {
            if (typeof window[fn] === 'function') {
                log(`✅ ${fn} está disponible`, 'success');
            } else {
                log(`❌ ${fn} NO está disponible`, 'error');
            }
        });
        
        if (typeof PANEL_CONFIG !== 'undefined') {
            log('✅ PANEL_CONFIG está disponible', 'success');
        } else {
            log('❌ PANEL_CONFIG NO está disponible', 'error');
        }
        
        log('=== PRUEBA COMPLETA FINALIZADA ===');
    }
    
    // Ejecución automática al cargar
    window.addEventListener('load', function() {
        log('🚀 Página cargada completamente');
        
        // Verificar archivos cargados
        const scripts = document.querySelectorAll('script[src]');
        log(`📦 ${scripts.length} scripts externos detectados`);
        
        testFunctions();
    });
    
    // Log inicial
    log('🔧 Inicializando pruebas...');
    </script>
</body>
</html>'''
    
    with open('test_panel_js.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Archivo de prueba generado: test_panel_js.html")
    print("   Para probar, abre este archivo en tu navegador")

if __name__ == "__main__":
    print("🧪 VERIFICADOR DE CONFIGURACIÓN DEL PANEL DE ENTRENAMIENTO")
    print("=" * 60)
    
    verificar_archivos_js()
    verificar_template()
    generar_html_prueba()
    
    print("✅ Verificación completada")
    print("\n📋 Próximos pasos:")
    print("1. Abre test_panel_js.html en tu navegador")
    print("2. Abre la consola del navegador (F12)")
    print("3. Haz clic en los botones de prueba")
    print("4. Revisa los logs en el output de la página")
