// Sistema de pruebas de automatizaciones
class AutomatizacionesTester {
    constructor() {
        this.datosPruebas = null;
        this.init();
    }

    init() {
        console.log('🚀 Sistema de pruebas de automatizaciones inicializado');
    }

    // Probar una automatización específica
    async probarAutomatizacion(automatizacionId, nombreAutomatizacion) {
        try {
            // Mostrar modal de progreso
            this.mostrarModalPrueba('iniciando', { nombre: nombreAutomatizacion });
            
            console.log(`🧪 Probando automatización: ${nombreAutomatizacion} (ID: ${automatizacionId})`);
            
            // Ejecutar la automatización específica
            const response = await fetch(`/panel_cliente/${window.nombreNora}/automatizaciones/api/ejecutar/${automatizacionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Automatización ejecutada:', data);
                this.mostrarModalPrueba('completado', {
                    nombre: nombreAutomatizacion,
                    resultado: data.resultado,
                    datos: data
                });
            } else {
                console.error('❌ Error en automatización:', data);
                this.mostrarModalPrueba('error', {
                    nombre: nombreAutomatizacion,
                    error: data.error,
                    datos: data
                });
            }
            
        } catch (error) {
            console.error('💥 Error ejecutando automatización:', error);
            this.mostrarModalPrueba('error', {
                nombre: nombreAutomatizacion,
                error: error.message
            });
        }
    }

    // Probar todo el sistema (función original)
    async probarSistemaCompleto() {
        try {
            // Mostrar modal de progreso
            this.mostrarModalPrueba('iniciando_sistema');
            
            console.log('🧪 Iniciando pruebas del sistema completo...');
            
            // Ejecutar pruebas del sistema
            const response = await fetch(`/panel_cliente/${window.nombreNora}/automatizaciones/api/probar-sistema`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Pruebas del sistema completadas:', data);
                this.mostrarModalPrueba('sistema_completado', data);
            } else {
                console.error('❌ Error en pruebas del sistema:', data);
                this.mostrarModalPrueba('error', data);
            }
            
        } catch (error) {
            console.error('💥 Error ejecutando pruebas del sistema:', error);
            this.mostrarModalPrueba('error', { error: error.message });
        }
    }

    mostrarModalPrueba(estado, datos = null) {
        // Crear o actualizar modal
        let modal = document.getElementById('modal-pruebas');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'modal-pruebas';
            modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            document.body.appendChild(modal);
        }
        
        let contenido = '';
        
        if (estado === 'iniciando') {
            contenido = `
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <div class="text-center">
                        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <h3 class="text-lg font-semibold mb-2">Ejecutando Automatización</h3>
                        <p class="text-gray-600">Probando: <strong>${datos.nombre}</strong></p>
                        <div class="mt-4 text-sm text-gray-500">
                            <p>• Validando configuración</p>
                            <p>• Importando módulo</p>
                            <p>• Ejecutando función</p>
                            <p>• Verificando resultado</p>
                        </div>
                    </div>
                </div>
            `;
        } else if (estado === 'iniciando_sistema') {
            contenido = `
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <div class="text-center">
                        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <h3 class="text-lg font-semibold mb-2">Ejecutando Pruebas del Sistema</h3>
                        <p class="text-gray-600">Verificando componentes de automatizaciones...</p>
                        <div class="mt-4 text-sm text-gray-500">
                            <p>• Conexión a base de datos</p>
                            <p>• Descubridor de funciones</p>
                            <p>• Sistema de ejecución</p>
                            <p>• APIs y frontend</p>
                        </div>
                    </div>
                </div>
            `;
        } else if (estado === 'completado') {
            const tiempoEjecucion = datos.datos?.tiempo_ejecucion || 'N/A';
            contenido = `
                <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
                    <div class="text-center mb-4">
                        <i class="fas fa-check-circle text-4xl text-green-600 mb-2"></i>
                        <h3 class="text-xl font-bold">Automatización Ejecutada</h3>
                        <p class="text-gray-600"><strong>${datos.nombre}</strong></p>
                    </div>
                    
                    <div class="mb-4">
                        <h4 class="font-semibold mb-2">Resultado:</h4>
                        <div class="bg-green-50 border border-green-200 rounded p-3 text-sm">
                            <pre class="whitespace-pre-wrap text-green-800">${JSON.stringify(datos.resultado, null, 2)}</pre>
                        </div>
                    </div>
                    
                    ${tiempoEjecucion !== 'N/A' ? `
                        <div class="mb-4 text-sm text-gray-600">
                            <span class="font-medium">Tiempo de ejecución:</span> ${tiempoEjecucion}
                        </div>
                    ` : ''}
                    
                    <div class="text-center">
                        <button onclick="automatizacionesTester.cerrarModal()" 
                                class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">
                            Cerrar
                        </button>
                    </div>
                </div>
            `;
        } else if (estado === 'sistema_completado') {
            const porcentaje = datos.porcentaje_exito || 0;
            const color = porcentaje >= 90 ? 'green' : porcentaje >= 70 ? 'yellow' : 'red';
            const icono = porcentaje >= 90 ? 'check-circle' : porcentaje >= 70 ? 'exclamation-triangle' : 'times-circle';
            
            contenido = `
                <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
                    <div class="text-center mb-4">
                        <i class="fas fa-${icono} text-4xl text-${color}-600 mb-2"></i>
                        <h3 class="text-xl font-bold">Pruebas del Sistema Completadas</h3>
                        <p class="text-gray-600">${datos.pruebas_exitosas}/${datos.total_pruebas} pruebas exitosas (${porcentaje}%)</p>
                    </div>
                    
                    <div class="mb-4">
                        <div class="bg-gray-200 rounded-full h-3">
                            <div class="bg-${color}-600 h-3 rounded-full" style="width: ${porcentaje}%"></div>
                        </div>
                    </div>
                    
                    ${datos.pruebas_detalle && datos.pruebas_detalle.length > 0 ? `
                        <div class="mb-4">
                            <h4 class="font-semibold mb-2">Detalle de Pruebas:</h4>
                            <div class="space-y-1 text-sm max-h-40 overflow-y-auto">
                                ${datos.pruebas_detalle.map(prueba => `
                                    <div class="flex items-center">
                                        <span class="mr-2">${prueba.icono}</span>
                                        <span class="${prueba.exitosa ? 'text-green-700' : 'text-red-700'}">${prueba.nombre}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="mb-4">
                        <h4 class="font-semibold mb-2">Estado del Sistema:</h4>
                        <span class="px-3 py-1 rounded-full text-sm font-medium ${
                            datos.estado_sistema === 'completamente_funcional' ? 'bg-green-100 text-green-800' :
                            datos.estado_sistema === 'mayormente_funcional' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                        }">
                            ${datos.estado_sistema === 'completamente_funcional' ? '🎉 Completamente Funcional' :
                              datos.estado_sistema === 'mayormente_funcional' ? '🟡 Mayormente Funcional' :
                              '🔴 Con Problemas'}
                        </span>
                    </div>
                    
                    <div class="text-center">
                        <button onclick="automatizacionesTester.cerrarModal()" 
                                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mr-2">
                            Cerrar
                        </button>
                        <button onclick="automatizacionesTester.mostrarLogCompleto()" 
                                class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg">
                            Ver Log Completo
                        </button>
                    </div>
                </div>
            `;
        } else if (estado === 'error') {
            contenido = `
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <div class="text-center">
                        <i class="fas fa-times-circle text-4xl text-red-600 mb-2"></i>
                        <h3 class="text-lg font-semibold mb-2 text-red-800">Error en la Ejecución</h3>
                        ${datos.nombre ? `<p class="text-gray-600 mb-2"><strong>${datos.nombre}</strong></p>` : ''}
                        <div class="bg-red-50 border border-red-200 rounded p-3 mb-4 text-sm">
                            <pre class="whitespace-pre-wrap text-red-800">${datos.error || 'Error desconocido'}</pre>
                        </div>
                        <button onclick="automatizacionesTester.cerrarModal()" 
                                class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg">
                            Cerrar
                        </button>
                    </div>
                </div>
            `;
        }
        
        modal.innerHTML = contenido;
        modal.style.display = 'flex';
        
        // Guardar datos para el log completo
        if (datos) {
            this.datosPruebas = datos;
        }
    }

    cerrarModal() {
        const modal = document.getElementById('modal-pruebas');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    mostrarLogCompleto() {
        if (!this.datosPruebas) return;
        
        const datos = this.datosPruebas;
        const ventana = window.open('', '_blank', 'width=800,height=600');
        
        ventana.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Log Completo de Pruebas - Automatizaciones</title>
                <style>
                    body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #fff; }
                    .timestamp { color: #888; }
                    .success { color: #0f0; }
                    .error { color: #f00; }
                    .warning { color: #ff0; }
                    pre { white-space: pre-wrap; line-height: 1.4; }
                </style>
            </head>
            <body>
                <h2>🧪 Log Completo de Pruebas del Sistema</h2>
                <p class="timestamp">Timestamp: ${datos.timestamp}</p>
                <p>Código de salida: ${datos.codigo_salida}</p>
                <p>Resultado: ${datos.pruebas_exitosas}/${datos.total_pruebas} pruebas exitosas (${datos.porcentaje_exito}%)</p>
                <hr>
                <h3>Salida Completa:</h3>
                <pre>${datos.salida_completa || 'Sin salida disponible'}</pre>
                ${datos.errores ? `
                    <hr>
                    <h3 class="error">Errores:</h3>
                    <pre class="error">${datos.errores}</pre>
                ` : ''}
            </body>
            </html>
        `);
        
        ventana.document.close();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Crear instancia global
    window.automatizacionesTester = new AutomatizacionesTester();
    
    // Cerrar modal al hacer click fuera
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('modal-pruebas');
        if (modal && e.target === modal) {
            window.automatizacionesTester.cerrarModal();
        }
    });
});

// Función global para probar automatización (llamada desde HTML)
function probarAutomatizacion(automatizacionId, nombreAutomatizacion) {
    if (window.automatizacionesTester) {
        window.automatizacionesTester.probarAutomatizacion(automatizacionId, nombreAutomatizacion);
    }
}

// Función global para probar sistema completo (llamada desde HTML)
function probarSistemaCompleto() {
    if (window.automatizacionesTester) {
        window.automatizacionesTester.probarSistemaCompleto();
    }
}
