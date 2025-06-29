/**
 * 🧪 DIAGNÓSTICO COMPLETO - Panel de Entrenamiento
 * Script para verificar todas las funcionalidades del panel
 */

console.log('🧪 DIAGNÓSTICO COMPLETO DEL PANEL DE ENTRENAMIENTO');
console.log('===================================================');

// 1. Verificar carga de scripts
console.log('\n1️⃣ VERIFICANDO CARGA DE SCRIPTS:');
const scripts = [
    '/static/js/ui-utils.js',
    '/static/js/conocimiento-manager.js',
    '/static/js/form-handlers.js',
    '/static/js/panel-entrenamiento-core.js'
];

scripts.forEach(script => {
    const elemento = document.querySelector(`script[src="${script}"]`);
    console.log(`   ${elemento ? '✅' : '❌'} ${script}`);
});

// 2. Verificar funciones globales
console.log('\n2️⃣ VERIFICANDO FUNCIONES GLOBALES:');
const funcionesRequeridas = {
    // UI Utils
    'initializeTabs': window.initializeTabs,
    'switchTab': window.switchTab,
    'setButtonLoading': window.setButtonLoading,
    'clearForm': window.clearForm,
    'scrollToSection': window.scrollToSection,
    'toggleExamples': window.toggleExamples,
    
    // Conocimiento Manager
    'cargarConocimiento': window.cargarConocimiento,
    'agregarBloque': window.agregarBloque,
    'eliminarBloque': window.eliminarBloque,
    'mostrarToast': window.mostrarToast,
    'configurarEventosConocimiento': window.configurarEventosConocimiento,
    'filtrarConocimiento': window.filtrarConocimiento,
    
    // Utils de formato
    'escapeHtml': window.escapeHtml,
    'formatDate': window.formatDate,
    'formatRelativeDate': window.formatRelativeDate
};

Object.entries(funcionesRequeridas).forEach(([nombre, funcion]) => {
    const disponible = typeof funcion === 'function';
    console.log(`   ${disponible ? '✅' : '❌'} ${nombre}: ${typeof funcion}`);
});

// 3. Verificar configuración global
console.log('\n3️⃣ VERIFICANDO CONFIGURACIÓN:');
console.log('   window.PANEL_CONFIG:', !!window.PANEL_CONFIG);
if (window.PANEL_CONFIG) {
    console.log('     - nombreNora:', window.PANEL_CONFIG.nombreNora);
    console.log('     - context:', window.PANEL_CONFIG.context);
    console.log('     - endpoints:', !!window.PANEL_CONFIG.endpoints);
    console.log('     - limits:', window.PANEL_CONFIG.limits);
}

console.log('   window.PANEL_STATE:', !!window.PANEL_STATE);
if (window.PANEL_STATE) {
    console.log('     - currentTab:', window.PANEL_STATE.currentTab);
    console.log('     - initialized:', window.PANEL_STATE.initialized);
}

// 4. Verificar elementos del DOM
console.log('\n4️⃣ VERIFICANDO ELEMENTOS DEL DOM:');
const elementosDOM = {
    // Pestañas
    'botones de pestañas': document.querySelectorAll('.tab-button'),
    'contenidos de pestañas': document.querySelectorAll('.tab-content'),
    'pestaña ver': document.querySelector('[data-tab="ver-conocimiento"]'),
    'pestaña agregar': document.querySelector('[data-tab="agregar-conocimiento"]'),
    'pestaña gestionar': document.querySelector('[data-tab="gestionar-etiquetas"]'),
    
    // Formulario agregar
    'formulario agregar': document.getElementById('form-agregar-conocimiento'),
    'contenido textarea': document.getElementById('nuevo-contenido'),
    'etiquetas input': document.getElementById('nuevas-etiquetas'),
    'prioridad checkbox': document.getElementById('nueva-prioridad'),
    'botón agregar': document.getElementById('btn-agregar-conocimiento'),
    'contador caracteres': document.getElementById('contador-caracteres'),
    
    // Lista conocimiento
    'lista conocimiento': document.getElementById('lista-conocimiento'),
    'buscar input': document.getElementById('buscar-conocimiento'),
    'filtro etiqueta': document.getElementById('filtro-etiqueta'),
    
    // Estadísticas
    'total bloques': document.getElementById('total-bloques'),
    'total etiquetas': document.getElementById('total-etiquetas'),
    'bloques prioritarios': document.getElementById('bloques-prioritarios')
};

Object.entries(elementosDOM).forEach(([nombre, elemento]) => {
    if (elemento && elemento.length !== undefined) {
        console.log(`   ✅ ${nombre}: ${elemento.length} elementos`);
    } else {
        const existe = elemento !== null;
        console.log(`   ${existe ? '✅' : '❌'} ${nombre}: ${existe ? 'Encontrado' : 'NO ENCONTRADO'}`);
    }
});

// 5. Verificar eventos configurados
console.log('\n5️⃣ VERIFICANDO EVENTOS:');
const formularioAgregar = document.getElementById('form-agregar-conocimiento');
if (formularioAgregar) {
    const tieneEventos = formularioAgregar.onsubmit !== null;
    console.log(`   ✅ Formulario agregar eventos: ${tieneEventos ? 'Configurados' : 'No configurados'}`);
}

const botonesPestañas = document.querySelectorAll('.tab-button');
let eventosConfigurados = 0;
botonesPestañas.forEach(boton => {
    if (boton.onclick !== null || boton.addEventListener) {
        eventosConfigurados++;
    }
});
console.log(`   ✅ Eventos de pestañas: ${eventosConfigurados}/${botonesPestañas.length} configurados`);

// 6. Funciones de prueba
console.log('\n6️⃣ FUNCIONES DE PRUEBA DISPONIBLES:');

function diagnosticarPestañas() {
    console.log('\n🔍 DIAGNÓSTICO ESPECÍFICO DE PESTAÑAS:');
    
    if (typeof window.initializeTabs === 'function') {
        console.log('   🔄 Reinicializando pestañas...');
        window.initializeTabs();
    }
    
    const pestañas = ['ver-conocimiento', 'agregar-conocimiento', 'gestionar-etiquetas'];
    pestañas.forEach((pestaña, index) => {
        setTimeout(() => {
            console.log(`   🧪 Probando pestaña: ${pestaña}`);
            if (typeof window.switchTab === 'function') {
                const botones = document.querySelectorAll('.tab-button');
                const contenidos = document.querySelectorAll('.tab-content');
                window.switchTab(pestaña, botones, contenidos);
                
                // Verificar resultado
                const activo = document.querySelector('.tab-button.active');
                const visible = document.querySelector('.tab-content:not(.hidden)');
                console.log(`      - Activo: ${activo?.getAttribute('data-tab')}`);
                console.log(`      - Visible: ${visible?.id}`);
            }
        }, index * 1000);
    });
}

function probarFormularioAgregar() {
    console.log('\n📝 PROBANDO FORMULARIO AGREGAR:');
    
    // Cambiar a pestaña agregar
    if (typeof window.switchTab === 'function') {
        const botones = document.querySelectorAll('.tab-button');
        const contenidos = document.querySelectorAll('.tab-content');
        window.switchTab('agregar-conocimiento', botones, contenidos);
    }
    
    // Llenar formulario
    const contenido = document.getElementById('nuevo-contenido');
    const etiquetas = document.getElementById('nuevas-etiquetas');
    const prioridad = document.getElementById('nueva-prioridad');
    
    if (contenido) {
        contenido.value = 'Contenido de prueba desde diagnóstico - ' + new Date().toLocaleTimeString();
        contenido.dispatchEvent(new Event('input'));
        console.log('   ✅ Contenido llenado');
    }
    
    if (etiquetas) {
        etiquetas.value = 'prueba, diagnóstico, test';
        console.log('   ✅ Etiquetas llenadas');
    }
    
    if (prioridad) {
        prioridad.checked = true;
        console.log('   ✅ Prioridad marcada');
    }
    
    console.log('   💡 Formulario listo para envío. Ejecuta simularEnvio() para probarlo.');
}

function simularEnvio() {
    console.log('\n🚀 SIMULANDO ENVÍO DEL FORMULARIO:');
    
    if (typeof window.agregarBloque === 'function') {
        window.agregarBloque();
        console.log('   ✅ Función agregarBloque ejecutada');
    } else {
        console.log('   ❌ agregarBloque no disponible');
    }
}

function cargarConocimientoManual() {
    console.log('\n📚 CARGANDO CONOCIMIENTO MANUALMENTE:');
    
    if (typeof window.cargarConocimiento === 'function') {
        window.cargarConocimiento().then(() => {
            console.log('   ✅ Conocimiento cargado exitosamente');
        }).catch(error => {
            console.log('   ❌ Error cargando conocimiento:', error.message);
        });
    } else {
        console.log('   ❌ cargarConocimiento no disponible');
    }
}

function reinicializarTodo() {
    console.log('\n🔄 REINICIALIZANDO SISTEMA COMPLETO:');
    
    // Reinicializar pestañas
    if (typeof window.initializeTabs === 'function') {
        window.initializeTabs();
        console.log('   ✅ Pestañas reinicializadas');
    }
    
    // Configurar eventos
    if (typeof window.configurarEventosConocimiento === 'function') {
        window.configurarEventosConocimiento();
        console.log('   ✅ Eventos de conocimiento configurados');
    }
    
    // Cargar conocimiento
    setTimeout(() => {
        if (typeof window.cargarConocimiento === 'function') {
            window.cargarConocimiento();
            console.log('   ✅ Conocimiento recargado');
        }
    }, 500);
}

// Exportar funciones de prueba
window.diagnosticarPestañas = diagnosticarPestañas;
window.probarFormularioAgregar = probarFormularioAgregar;
window.simularEnvio = simularEnvio;
window.cargarConocimientoManual = cargarConocimientoManual;
window.reinicializarTodo = reinicializarTodo;

console.log('\n💡 COMANDOS DISPONIBLES:');
console.log('   - diagnosticarPestañas()     : Prueba el sistema de pestañas');
console.log('   - probarFormularioAgregar()  : Llena y prueba el formulario');
console.log('   - simularEnvio()             : Simula envío del formulario');
console.log('   - cargarConocimientoManual() : Recarga el conocimiento');
console.log('   - reinicializarTodo()        : Reinicializa todo el sistema');

console.log('\n===================================================');
console.log('🧪 DIAGNÓSTICO COMPLETADO');
console.log('💡 Ejecuta reinicializarTodo() si hay problemas');

// Auto-reinicialización si hay problemas detectados
const problemas = [];
if (typeof window.switchTab !== 'function') problemas.push('switchTab');
if (typeof window.agregarBloque !== 'function') problemas.push('agregarBloque');
if (typeof window.initializeTabs !== 'function') problemas.push('initializeTabs');

if (problemas.length > 0) {
    console.log(`\n⚠️  PROBLEMAS DETECTADOS: ${problemas.join(', ')}`);
    console.log('🔄 Ejecutando reinicialización automática en 2 segundos...');
    setTimeout(reinicializarTodo, 2000);
} else {
    console.log('\n✅ SISTEMA FUNCIONANDO CORRECTAMENTE');
    console.log('🎯 Ejecutando diagnóstico de pestañas...');
    setTimeout(diagnosticarPestañas, 1000);
}
