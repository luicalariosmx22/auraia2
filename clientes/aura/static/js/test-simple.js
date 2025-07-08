// TEST SIMPLE - Solo exportar función
console.log('🧪 TEST SIMPLE cargado');

function cargarConocimientoTest() {
    console.log('🎯 cargarConocimientoTest ejecutada!');
    alert('¡Función funciona!');
    return 'Función ejecutada correctamente';
}

// Exportar inmediatamente
window.cargarConocimientoTest = cargarConocimientoTest;
console.log('✅ cargarConocimientoTest exportada:', typeof window.cargarConocimientoTest);

// Verificar que realmente esté en window
console.log('🔍 Verificando window.cargarConocimientoTest:', window.cargarConocimientoTest);
