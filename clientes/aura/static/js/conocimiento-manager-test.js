/**
 * 🧪 TEST SIMPLE - CONOCIMIENTO MANAGER
 * Version mínima para debugging
 */

console.log('🧪 TEST SIMPLE - CONOCIMIENTO MANAGER cargando...');

// Test básico de exportación
function cargarConocimientoTest() {
    console.log('🎯 cargarConocimientoTest ejecutada!');
    alert('✅ cargarConocimientoTest funciona!');
    return 'Test exitoso';
}

// Exportar inmediatamente
window.cargarConocimiento = cargarConocimientoTest;
window.cargarConocimientoTest = cargarConocimientoTest;

console.log('✅ Funciones exportadas:', {
    cargarConocimiento: typeof window.cargarConocimiento,
    cargarConocimientoTest: typeof window.cargarConocimientoTest
});

console.log('🎉 TEST SIMPLE completado');
