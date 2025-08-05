// Configuración global
const config = {
    nombreNora: window.nombreNora,
    metaAdsBaseUrl: `/panel_cliente/${window.nombreNora}/meta_ads`,
    endpoints: {
        importarMeta: '/importar_desde_meta',
        testConexion: (cuentaId) => `/cuentas_publicitarias/${window.nombreNora}/${cuentaId}/test_conexion`,
        adsActivos: (cuentaId) => `/cuentas_publicitarias/${window.nombreNora}/${cuentaId}/ads_activos`
    }
};

// Estado de la aplicación
const state = {
    cuentaActual: null,
    ultimoError: null,
    startTime: null
};

// Utilidades
const utils = {
    actualizarUI(elemento, config) {
        Object.entries(config).forEach(([prop, valor]) => {
            elemento[prop] = valor;
        });
    },

    async esperarTiempo(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// Manejadores de UI
const ui = {
    actualizarPaso(paso, estado, mensaje = '') {
        const li = document.querySelector(`[data-paso="${paso}"]`);
        const circle = li.querySelector('.w-6');
        const estadoSpan = li.querySelector('.paso-estado');
        
        circle.className = 'w-6 h-6 flex-shrink-0 rounded-full flex items-center justify-center ';
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

        document.getElementById('btn-reintentar').classList.remove('hidden');
    },

    mostrarExito(detalles) {
        const detallesExito = document.getElementById('detalles-exito');
        detallesExito.classList.remove('hidden');
        detallesExito.querySelector('div').innerHTML = Object.entries(detalles)
            .map(([key, value]) => `<div><strong>${key}:</strong> ${value}</div>`)
            .join('');
    },

    generarMensajeError(mensaje, paso) {
        // ... resto del código de generación de mensaje de error ...
    }
};

// Controladores de eventos
const handlers = {
    async actualizarCuentas(event) {
        const btn = event.target;
        utils.actualizarUI(btn, {
            disabled: true,
            textContent: 'Actualizando...'
        });

        try {
            const resp = await fetch(window.location.pathname);
            if (resp.ok) {
                const data = await resp.json();
                await this.manejarRespuestaActualizacion(data, btn);
                
                // Mostrar notificación si hay cuentas inactivas
                if (data.alertas_generadas && data.alertas_generadas > 0) {
                    const mensaje = `Se han detectado ${data.alertas_generadas} cuenta${data.alertas_generadas > 1 ? 's' : ''} inactiva${data.alertas_generadas > 1 ? 's' : ''}.`;
                    const notificacion = document.createElement('div');
                    notificacion.className = 'fixed bottom-4 right-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded shadow-lg';
                    notificacion.innerHTML = `
                        <div class="flex items-center">
                            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                            </svg>
                            <p>${mensaje}</p>
                        </div>
                    `;
                    document.body.appendChild(notificacion);
                    setTimeout(() => notificacion.remove(), 5000);
                }
            } else {
                await this.manejarErrorActualizacion(resp, btn);
            }
        } catch (e) {
            alert('Error de red al actualizar las cuentas');
            utils.actualizarUI(btn, {
                disabled: false,
                textContent: 'Actualizar cuentas'
            });
        }
    },

    async importarDesdeMeta(event) {
        const btn = event.target;
        utils.actualizarUI(btn, {
            disabled: true,
            textContent: 'Importando...'
        });

        try {
            const resp = await fetch(config.endpoints.importarMeta, { method: 'POST' });
            const data = await resp.json();
            
            if (resp.ok && data.ok) {
                btn.textContent = `¡Importadas: ${data.agregadas}!`;
                btn.classList.remove('bg-purple-600', 'hover:bg-purple-800');
                btn.classList.add('bg-green-600');
                setTimeout(() => location.reload(), 900);
            } else {
                alert('Error al importar: ' + (data.msg || resp.statusText));
                utils.actualizarUI(btn, {
                    disabled: false,
                    textContent: 'Importar desde Meta'
                });
            }
        } catch (e) {
            alert('Error de red al importar cuentas');
            utils.actualizarUI(btn, {
                disabled: false,
                textContent: 'Importar desde Meta'
            });
        }
    }
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar manejadores de eventos
    document.getElementById('btn-actualizar-cuentas').onclick = handlers.actualizarCuentas;
    document.getElementById('btn-importar-meta').onclick = handlers.importarDesdeMeta;
    
    // Inicializar filtros
    ['input', 'change'].forEach(evento => {
        document.getElementById('filtro-empresa').addEventListener(evento, () => filtros.aplicar());
        document.getElementById('filtro-estado').addEventListener(evento, () => filtros.aplicar());
        document.getElementById('filtro-vinculo').addEventListener(evento, () => filtros.aplicar());
        document.getElementById('filtro-anuncios').addEventListener(evento, () => filtros.aplicar());
    });

    // Inicializar modal (comentado hasta que se defina la función)
    // initModal();
});

const btnActualizarCuentas = {
    async onClick() {
        const btn = document.getElementById('btn-actualizar-cuentas');
        btn.disabled = true;
        btn.textContent = 'Actualizando...';
        try {
            const resp = await fetch(window.location.pathname + '/actualizar', { method: 'POST' });
            if (resp.ok) {
                const data = await resp.json().catch(() => ({}));
                if (data && data.ok && data.cuentas) {
                    this.actualizarFilasCuentas(data.cuentas);
                    this.mostrarExitoActualizacion(btn);
                } else {
                    this.recargarPagina(btn);
                }
            } else {
                this.manejarError(btn, resp);
            }
        } catch (e) {
            alert('Error de red al actualizar las cuentas');
            this.resetearBoton(btn);
        }
    },

    actualizarFilasCuentas(cuentas) {
        for (const cuenta of cuentas) {
            const span = document.getElementById('ads-activos-' + cuenta.id_cuenta_publicitaria);
            if (span && span.textContent != cuenta.ads_activos) {
                span.textContent = cuenta.ads_activos;
                span.classList.add('text-green-700', 'font-bold');
                setTimeout(() => span.classList.remove('text-green-700', 'font-bold'), 1200);
            }
            if (cuenta.nombre_cliente) {
                this.actualizarNombreCuenta(cuenta);
            }
        }
    },

    actualizarNombreCuenta(cuenta) {
        const nombreTd = document.querySelector(
            `#ads-activos-${cuenta.id_cuenta_publicitaria}`
        )?.closest('tr')?.querySelector('td:nth-child(2)');
        if (nombreTd) {
            const br = nombreTd.querySelector('br');
            if (br && br.previousSibling) {
                br.previousSibling.textContent = cuenta.nombre_cliente;
            } else {
                nombreTd.childNodes[0].textContent = cuenta.nombre_cliente;
            }
        }
    },

    mostrarExitoActualizacion(btn) {
        btn.textContent = '¡Actualizado!';
        btn.classList.remove('bg-blue-500', 'hover:bg-blue-700');
        btn.classList.add('bg-green-600');
        setTimeout(() => this.resetearBoton(btn), 1200);
    },

    recargarPagina(btn) {
        btn.textContent = '¡Actualizado!';
        setTimeout(() => location.reload(), 700);
    },

    async manejarError(btn, resp) {
        const data = await resp.json().catch(() => ({}));
        let msg = 'Error al actualizar las cuentas';
        if (data && data.errores && data.errores.length > 0) {
            msg += '\n' + data.errores.map(e => `Cuenta ${e.cuenta_id}: ${e.error}`).join('\n');
        }
        alert(msg);
        this.resetearBoton(btn);
    },

    resetearBoton(btn) {
        btn.disabled = false;
        btn.textContent = 'Actualizar cuentas';
        btn.classList.remove('bg-green-600');
        btn.classList.add('bg-blue-500', 'hover:bg-blue-700');
    }
};

const btnImportarMeta = {
    async onClick() {
        const btn = document.getElementById('btn-importar-meta');
        btn.disabled = true;
        btn.textContent = 'Importando...';
        try {
            const resp = await fetch(window.location.pathname + '/importar_desde_meta', { method: 'POST' });
            const data = await resp.json();
            if (resp.ok && data.ok) {
                this.mostrarExitoImportacion(btn, data.agregadas);
            } else {
                this.manejarError(btn, data, resp);
            }
        } catch (e) {
            alert('Error de red al importar cuentas');
            this.resetearBoton(btn);
        }
    },

    mostrarExitoImportacion(btn, agregadas) {
        btn.textContent = `¡Importadas: ${agregadas}!`;
        btn.classList.remove('bg-purple-600', 'hover:bg-purple-800');
        btn.classList.add('bg-green-600');
        setTimeout(() => location.reload(), 900);
    },

    manejarError(btn, data, resp) {
        alert('Error al importar: ' + (data.msg || resp.statusText));
        this.resetearBoton(btn);
    },

    resetearBoton(btn) {
        btn.disabled = false;
        btn.textContent = 'Importar desde Meta';
    }
};

// Funciones de utilidad para manejar cuentas
const cuentasUtils = {
    actualizarAdsActivos(cuentaId) {
        const span = document.getElementById('ads-activos-' + cuentaId);
        const old = span.textContent;
        span.textContent = '...';
        fetch(`/panel_cliente/${config.nombreNora}/meta_ads/cuentas_publicitarias/${config.nombreNora}/${cuentaId}/ads_activos`)
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    span.textContent = data.ads_activos;
                    span.classList.add('text-green-700');
                    setTimeout(() => span.classList.remove('text-green-700'), 1200);
                } else {
                    span.textContent = old;
                    alert('Error al actualizar ads activos');
                }
            })
            .catch(() => {
                span.textContent = old;
                alert('Error de red al actualizar ads activos');
            });
    }
};

// Sistema de filtrado
const filtros = {
    aplicar() {
        const empresa = document.getElementById('filtro-empresa').value.toLowerCase();
        const estado = document.getElementById('filtro-estado').value;
        const vinculo = document.getElementById('filtro-vinculo').value;
        const anuncios = document.getElementById('filtro-anuncios').value;
        
        document.querySelectorAll('tbody tr').forEach(tr => {
            if (tr.querySelector('td')?.classList.contains('text-gray-400')) return;
            let mostrar = true;
            
            if (empresa) mostrar = this.aplicarFiltroEmpresa(tr, empresa);
            if (mostrar && estado) mostrar = this.aplicarFiltroEstado(tr, estado);
            if (mostrar && vinculo) mostrar = this.aplicarFiltroVinculo(tr, vinculo);
            if (mostrar && anuncios) mostrar = this.aplicarFiltroAnuncios(tr, anuncios);
            
            tr.style.display = mostrar ? '' : 'none';
        });
    },

    aplicarFiltroEmpresa(tr, empresa) {
        const empresaCell = tr.querySelector('td:first-child').innerText.toLowerCase();
        const cuentaCell = tr.querySelector('td:nth-child(2)').innerText.toLowerCase();
        return empresaCell.includes(empresa) || cuentaCell.includes(empresa);
    },

    aplicarFiltroEstado(tr, estado) {
        const esActiva = tr.querySelector('td:nth-child(3) span')?.textContent.includes('Activa');
        return (estado === '1' && esActiva) || (estado === '0' && !esActiva);
    },

    aplicarFiltroVinculo(tr, vinculo) {
        const vincularBtn = tr.querySelector('td:last-child a').textContent.trim();
        const tieneEmpresa = vincularBtn === 'Cambiar';
        return (vinculo === 'con_empresa' && tieneEmpresa) || (vinculo === 'sin_empresa' && !tieneEmpresa);
    },

    aplicarFiltroAnuncios(tr, anuncios) {
        const span = tr.querySelector('td:nth-child(4) span');
        const val = span ? span.textContent.trim() : '';
        if (anuncios === 'con_activos') {
            return val && val !== '—' && val !== '0';
        } else {
            return !val || val === '—' || val === '0';
        }
    }
};

// Diagnóstico y modal
const diagnostico = {
    cuentaActual: null,
    ultimoError: null,
    startTime: null,
    modal: null,

    async probarConexion(cuentaId) {
        this.startTime = Date.now();
        this.cuentaActual = cuentaId;
        const estadoSpan = document.getElementById(`conexion-estado-${cuentaId}`);
        const dot = estadoSpan.querySelector('.rounded-full');
        const text = estadoSpan.querySelector('.text-sm');

        this.abrirModal();
        await this.ejecutarPrueba(cuentaId, dot, text);
    },

    async ejecutarPrueba(cuentaId, dot, text) {
        try {
            this.mostrarInfoCuenta(cuentaId);
            this.actualizarUIEstadoPrueba(dot, text);
            await this.realizarPrueba(cuentaId);
        } catch (e) {
            this.manejarError(e, dot, text);
        }
    },

    mostrarInfoCuenta(cuentaId) {
        const nombreCuenta = document.querySelector(`#ads-activos-${cuentaId}`).closest('tr').querySelector('td:nth-child(2)').textContent;
        document.getElementById('modal-cuenta-info').textContent = `${nombreCuenta} (ID: ${cuentaId})`;
    },

    actualizarUIEstadoPrueba(dot, text) {
        dot.className = 'w-2 h-2 rounded-full bg-yellow-400 animate-pulse';
        text.textContent = 'Probando...';
        this.actualizarPasos('progreso');
    },

    async realizarPrueba(cuentaId) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        try {
            const response = await fetch(
                `/panel_cliente/${config.nombreNora}/meta_ads/cuentas_publicitarias/${config.nombreNora}/${cuentaId}/test_conexion`,
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
                await this.procesarExito(data);
            } else {
                throw new Error(data.error || 'Error desconocido en la conexión');
            }
        } catch (error) {
            throw error;
        }
    },

    async procesarExito(data) {
        await this.actualizarPasosExitosos(data);
        this.mostrarDetallesExito(data);
    },

    manejarError(e, dot, text) {
        console.error('Error general:', e);
        const errorMessage = e.name === 'AbortError'
            ? 'Tiempo de espera agotado en la conexión'
            : e.message;

        this.actualizarPaso('token', 'error', errorMessage);
        dot.className = 'w-2 h-2 rounded-full bg-red-500';
        text.textContent = 'Error';
        this.mostrarError(errorMessage);
        document.getElementById('btn-reintentar').classList.remove('hidden');
    },

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

        estados[estado]();
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Botones principales
    document.getElementById('btn-actualizar-cuentas').onclick = () => btnActualizarCuentas.onClick();
    document.getElementById('btn-importar-meta').onclick = () => btnImportarMeta.onClick();

    // Filtros
    document.getElementById('filtro-empresa').addEventListener('input', () => filtros.aplicar());
    document.getElementById('filtro-estado').addEventListener('change', () => filtros.aplicar());
    document.getElementById('filtro-vinculo').addEventListener('change', () => filtros.aplicar());
    document.getElementById('filtro-anuncios').addEventListener('change', () => filtros.aplicar());

    // Modal
    const modal = document.getElementById('modal-diagnostico');
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            diagnostico.cerrarModal();
        }
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            diagnostico.cerrarModal();
        }
    });
});
