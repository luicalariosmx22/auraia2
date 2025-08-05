// Configuración del diagnóstico
const diagnosticoConfig = {
    pasos: ['token', 'cuenta', 'permisos', 'anuncios'],
    pasosDescripcion: {
        token: {
            titulo: 'Verificación de Token de Acceso',
            descripcion: 'Verifica que el token de acceso sea válido y esté activo',
            solucion: 'Renueva el token de acceso en Meta Business Manager'
        },
        cuenta: {
            titulo: 'Acceso a la Cuenta',
            descripcion: 'Verifica el acceso a la cuenta publicitaria',
            solucion: 'Verifica los permisos en Meta Business Manager'
        },
        permisos: {
            titulo: 'Verificación de Permisos',
            descripcion: 'Verifica los permisos necesarios para gestionar anuncios',
            solucion: 'Solicita los permisos necesarios al administrador de la cuenta'
        },
        anuncios: {
            titulo: 'Acceso a Anuncios',
            descripcion: 'Verifica el acceso a los anuncios de la cuenta',
            solucion: 'Verifica que la cuenta tenga anuncios activos'
        }
    },
    timeout: 15000
};

// Estado global del diagnóstico
const diagnosticoState = {
    cuentaActual: null,
    ultimoError: null,
    startTime: null
};

// Clase principal del diagnóstico
class Diagnostico {
    constructor() {
        this.bindEvents();
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action="probar-conexion"]');
            if (btn) {
                const cuentaId = btn.dataset.cuentaId;
                this.probarConexion(cuentaId);
            }
        });
    }

    async probarConexion(cuentaId) {
        diagnosticoState.startTime = Date.now();
        diagnosticoState.cuentaActual = cuentaId;
        const estadoSpan = document.getElementById(`conexion-estado-${cuentaId}`);
        const dot = estadoSpan.querySelector('.rounded-full');
        const text = estadoSpan.querySelector('.text-sm');
        
        modal.abrir();
        
        try {
            const nombreCuenta = document.querySelector(`#ads-activos-${cuentaId}`).closest('tr').querySelector('td:nth-child(2)').textContent;
            document.getElementById('modal-cuenta-info').textContent = `${nombreCuenta} (ID: ${cuentaId})`;
            
            dot.className = 'w-2 h-2 rounded-full bg-yellow-400 animate-pulse';
            text.textContent = 'Probando...';

            await this.ejecutarPruebas(cuentaId, dot, text);
        } catch (e) {
            this.manejarError(e, dot, text);
        }
    }

    async ejecutarPruebas(cuentaId, dot, text) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), diagnosticoConfig.timeout);
        
        try {
            const response = await fetch(
                `/panel_cliente/${window.appConfig.nombreNora}/meta_ads/cuentas_publicitarias/${window.appConfig.nombreNora}/${cuentaId}/test_conexion`,
                { 
                    signal: controller.signal,
                    headers: {
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    }
                }
            );
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.ok) {
                await this.procesarExito(data, dot, text);
            } else {
                throw new Error(data.error || 'Error desconocido en la conexión');
            }
        } catch (error) {
            throw error;
        }
    }

    async procesarExito(data, dot, text) {
        const updateSteps = [
            { step: 'token', delay: 0 },
            { step: 'cuenta', delay: 500 },
            { step: 'permisos', delay: 500, message: data.detalles?.permisos || 'Básicos' },
            { step: 'anuncios', delay: 500, message: `${data.detalles?.activos || 0} activos` }
        ];

        for (const { step, delay, message } of updateSteps) {
            ui.actualizarPaso(step, 'progreso');
            if (delay) await utils.esperarTiempo(delay);
            ui.actualizarPaso(step, 'exito', message);
        }

        dot.className = 'w-2 h-2 rounded-full bg-green-500';
        text.textContent = 'Conectada';
        
        ui.mostrarExito({
            'Estado de la cuenta': data.status || 'Activa',
            'Anuncios activos': data.detalles?.activos || 0,
            'Última actualización': new Date().toLocaleString(),
            'Tiempo de respuesta': `${Date.now() - diagnosticoState.startTime}ms`,
            'Detalles adicionales': data.detalles?.mensaje || 'Conexión exitosa'
        });
    }

    manejarError(e, dot, text) {
        console.error('Error general:', e);
        const errorMessage = e.name === 'AbortError' 
            ? 'Tiempo de espera agotado en la conexión'
            : e.message;
        
        ui.actualizarPaso('token', 'error', errorMessage);
        dot.className = 'w-2 h-2 rounded-full bg-red-500';
        text.textContent = 'Error';
        ui.mostrarError(errorMessage);
        document.getElementById('btn-reintentar').classList.remove('hidden');
    }

    reintentar() {
        if (diagnosticoState.cuentaActual) {
            document.getElementById('btn-reintentar').classList.add('hidden');
            document.getElementById('detalles-error').classList.add('hidden');
            document.getElementById('detalles-exito').classList.add('hidden');
            diagnosticoConfig.pasos.forEach(paso => ui.actualizarPaso(paso, 'pendiente'));
            this.probarConexion(diagnosticoState.cuentaActual);
        }
    }
}

// UI helpers
const ui = {
    actualizarPaso(paso, estado, mensaje = '') {
        const li = document.querySelector(`[data-paso="${paso}"]`);
        const circle = li.querySelector('.w-6');
        const estadoSpan = li.querySelector('.paso-estado');
        
        circle.className = 'w-6 h-6 flex-shrink-0 rounded-full flex items-center justify-center';
        estadoSpan.className = 'paso-estado ml-auto text-sm';
        
        const estados = {
            pendiente: () => {
                circle.classList.add('border-2', 'border-gray-300');
                estadoSpan.textContent = '';
            },
            progreso: () => {
                circle.classList.add('border-2', 'border-yellow-400', 'animate-pulse');
                estadoSpan.textContent = 'Verificando...';
                estadoSpan.classList.add('text-yellow-600');
            },
            error: () => {
                circle.classList.add('bg-red-500', 'text-white');
                estadoSpan.textContent = mensaje || 'Error';
                estadoSpan.classList.add('text-red-600');
            },
            exito: () => {
                circle.classList.add('bg-green-500', 'text-white');
                estadoSpan.textContent = mensaje || 'OK';
                estadoSpan.classList.add('text-green-600');
            }
        };

        estados[estado]?.();
    },

    mostrarError(mensaje, paso = 'token') {
        const detallesError = document.getElementById('detalles-error');
        detallesError.classList.remove('hidden');
        const errorDiv = detallesError.querySelector('pre');
        
        const mensajeCompleto = this.generarMensajeError(mensaje, paso);
        errorDiv.textContent = mensajeCompleto;
    },

    generarMensajeError(mensaje, paso) {
        const isNetworkError = mensaje.toLowerCase().includes('error de red');
        let mensajeCompleto = '📋 Diagnóstico del Error:\n------------------------\n';
        mensajeCompleto += `Error: ${mensaje}\n\n`;
        
        if (isNetworkError) {
            mensajeCompleto += this.generarEstadoConectividad();
        }
        
        if (diagnosticoConfig.pasosDescripcion[paso]) {
            mensajeCompleto += this.generarContextoError(paso, isNetworkError);
        }

        mensajeCompleto += this.generarPasosVerificacion(paso);
        mensajeCompleto += this.generarAccionesRecomendadas(isNetworkError);
        mensajeCompleto += '\n⏰ Timestamp: ' + new Date().toLocaleString();
        
        return mensajeCompleto;
    },

    generarEstadoConectividad() {
        return '🌐 Estado de Conectividad:\n- Verificando conexión a internet...\n';
    },

    generarContextoError(paso, isNetworkError) {
        let mensaje = '\n🔍 Contexto:\n';
        mensaje += `${diagnosticoConfig.pasosDescripcion[paso].descripcion}\n\n`;
        mensaje += '💡 Solución Sugerida:\n';
        mensaje += `${diagnosticoConfig.pasosDescripcion[paso].solucion}\n`;
        
        if (isNetworkError) {
            mensaje += '• Verifica tu conexión a internet\n';
            mensaje += '• Confirma que puedas acceder a business.facebook.com\n';
            mensaje += '• Verifica que no haya restricciones de firewall\n';
        }
        
        return mensaje;
    },

    generarPasosVerificacion(pasoActual) {
        let mensaje = '\n📌 Pasos de Verificación:\n';
        let pasoEncontrado = false;
        
        for (const paso of diagnosticoConfig.pasos) {
            const estado = paso === pasoActual ? '❌' : (!pasoEncontrado ? '✅' : '⭕');
            mensaje += `${estado} ${diagnosticoConfig.pasosDescripcion[paso].titulo}${paso === pasoActual ? ' <- Error aquí' : ''}\n`;
            if (paso === pasoActual) pasoEncontrado = true;
        }
        
        return mensaje;
    },

    generarAccionesRecomendadas(isNetworkError) {
        let mensaje = '\n🔧 Acciones Recomendadas:\n';
        mensaje += isNetworkError ? 
            '1. ✨ Verifica tu conexión a internet\n' +
            '2. 🔄 Intenta recargar la página\n' +
            '3. 🛡️ Revisa la configuración del firewall\n' +
            '4. 📞 Si persiste, contacta al soporte técnico\n' :
            '1. 🔑 Verifica las credenciales de Meta\n' +
            '2. 📅 Comprueba que el token no haya expirado\n' +
            '3. 👥 Revisa los permisos en Meta Business Manager\n' +
            '4. 📞 Si el problema persiste, contacta al soporte\n';
        
        return mensaje;
    },

    mostrarExito(detalles) {
        const detallesExito = document.getElementById('detalles-exito');
        detallesExito.classList.remove('hidden');
        detallesExito.querySelector('div').innerHTML = Object.entries(detalles)
            .map(([key, value]) => `<div><strong>${key}:</strong> ${value}</div>`)
            .join('');
    }
};

// Utilidades
const utils = {
    async esperarTiempo(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    copiarDiagnostico() {
        const diagnostico = document.querySelector('#detalles-error pre').textContent;
        navigator.clipboard.writeText(diagnostico).then(() => {
            const btn = document.querySelector('#detalles-error button');
            const originalText = btn.innerHTML;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>Copiado!`;
            setTimeout(() => btn.innerHTML = originalText, 2000);
        });
    },

    abrirDocumentacion() {
        window.open('https://developers.facebook.com/docs/marketing-api/error-reference/', '_blank');
    }
};

// Inicializar el diagnóstico cuando el documento esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.diagnostico = new Diagnostico();
});
