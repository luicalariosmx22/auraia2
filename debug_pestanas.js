// 🧪 SCRIPT DE DEPURACIÓN - Sistema de Pestañas
console.log('🧪 INICIANDO DIAGNÓSTICO DE PESTAÑAS...');
console.log('============================================');

// 1. Verificar elementos del DOM
console.log('\n1️⃣ VERIFICANDO ELEMENTOS DEL DOM:');
const elementos = {
    'pestañas (botones)': document.querySelectorAll('.tab-button'),
    'contenidos': document.querySelectorAll('.tab-content'),
    'ver-conocimiento': document.querySelector('[data-tab="ver-conocimiento"]'),
    'agregar-conocimiento': document.querySelector('[data-tab="agregar-conocimiento"]'),
    'gestionar-etiquetas': document.querySelector('[data-tab="gestionar-etiquetas"]'),
    'tab-ver-conocimiento': document.getElementById('tab-ver-conocimiento'),
    'tab-agregar-conocimiento': document.getElementById('tab-agregar-conocimiento'),
    'tab-gestionar-etiquetas': document.getElementById('tab-gestionar-etiquetas')
};

Object.entries(elementos).forEach(([nombre, elemento]) => {
    if (elemento && elemento.length !== undefined) {
        // Es una NodeList
        console.log(`   ✅ ${nombre}: ${elemento.length} elementos encontrados`);
    } else {
        const existe = elemento !== null;
        console.log(`   ${existe ? '✅' : '❌'} ${nombre}: ${existe ? 'Encontrado' : 'NO ENCONTRADO'}`);
    }
});

// 2. Verificar funciones del sistema de pestañas
console.log('\n2️⃣ VERIFICANDO FUNCIONES:');
const funciones = {
    switchTab: window.switchTab,
    initializeTabs: window.initializeTabs,
    handleTabSwitch: window.handleTabSwitch
};

Object.entries(funciones).forEach(([nombre, funcion]) => {
    const disponible = typeof funcion === 'function';
    console.log(`   ${disponible ? '✅' : '❌'} ${nombre}: ${typeof funcion}`);
});

// 3. Verificar estado global
console.log('\n3️⃣ VERIFICANDO ESTADO:');
console.log('   window.PANEL_STATE:', window.PANEL_STATE);

// 4. Verificar eventos de clic
console.log('\n4️⃣ VERIFICANDO EVENTOS:');
const botonesPestañas = document.querySelectorAll('.tab-button');
botonesPestañas.forEach((boton, index) => {
    const dataTabs = boton.getAttribute('data-tab');
    const hasEvents = boton.onclick !== null || boton._listeners;
    console.log(`   Botón ${index + 1}: data-tab="${dataTabs}", eventos: ${hasEvents ? 'Sí' : 'No'}`);
});

// 5. Función para probar cambio de pestañas
console.log('\n5️⃣ FUNCIONES DE PRUEBA DISPONIBLES:');

function probarPestaña(nombrePestaña) {
    console.log(`\n🧪 PROBANDO PESTAÑA: ${nombrePestaña}`);
    
    if (typeof window.switchTab === 'function') {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        console.log(`   - Botones encontrados: ${tabButtons.length}`);
        console.log(`   - Contenidos encontrados: ${tabContents.length}`);
        
        window.switchTab(nombrePestaña, tabButtons, tabContents);
        
        // Verificar resultado
        const botonActivo = document.querySelector('.tab-button.active');
        const contenidoVisible = document.querySelector('.tab-content:not(.hidden)');
        
        console.log(`   - Botón activo: ${botonActivo ? botonActivo.getAttribute('data-tab') : 'Ninguno'}`);
        console.log(`   - Contenido visible: ${contenidoVisible ? contenidoVisible.id : 'Ninguno'}`);
        
        return {
            botonActivo: botonActivo?.getAttribute('data-tab'),
            contenidoVisible: contenidoVisible?.id
        };
    } else {
        console.error('   ❌ switchTab no está disponible');
        return null;
    }
}

function reinicializarPestañas() {
    console.log('\n🔄 REINICIALIZANDO PESTAÑAS...');
    
    if (typeof window.initializeTabs === 'function') {
        window.initializeTabs();
        console.log('   ✅ Pestañas reinicializadas');
        
        // Verificar eventos después de reinicializar
        const botones = document.querySelectorAll('.tab-button');
        botones.forEach((boton, index) => {
            const eventos = boton.onclick !== null;
            console.log(`   Botón ${index + 1} eventos: ${eventos ? 'Sí' : 'No'}`);
        });
    } else {
        console.error('   ❌ initializeTabs no está disponible');
    }
}

function probarTodas() {
    console.log('\n🚀 PROBANDO TODAS LAS PESTAÑAS...');
    const pestañas = ['ver-conocimiento', 'agregar-conocimiento', 'gestionar-etiquetas'];
    
    pestañas.forEach((pestaña, index) => {
        setTimeout(() => {
            console.log(`\n--- Probando ${pestaña} ---`);
            probarPestaña(pestaña);
        }, index * 1000);
    });
}

// Hacer funciones disponibles globalmente
window.probarPestaña = probarPestaña;
window.reinicializarPestañas = reinicializarPestañas;
window.probarTodas = probarTodas;

console.log('\n💡 COMANDOS DISPONIBLES:');
console.log('   - probarPestaña("ver-conocimiento")');
console.log('   - probarPestaña("agregar-conocimiento")');
console.log('   - probarPestaña("gestionar-etiquetas")');
console.log('   - reinicializarPestañas()');
console.log('   - probarTodas()');

console.log('\n============================================');
console.log('🧪 DIAGNÓSTICO DE PESTAÑAS COMPLETADO');

// Auto-prueba básica
console.log('\n🔍 EJECUTANDO AUTO-PRUEBA...');
setTimeout(() => {
    reinicializarPestañas();
    setTimeout(() => {
        probarPestaña('agregar-conocimiento');
    }, 500);
}, 1000);
