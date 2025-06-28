/**
 * 🧠 CONOCIMIENTO MANAGER - Gestión de Bloques de Conocimiento
 * Funciones para cargar, crear, editar y eliminar bloques de conocimiento
 */

console.log('📚 CONOCIMIENTO MANAGER iniciando carga - versión 1.1');
console.log('🔍 window disponible al inicio:', typeof window !== 'undefined');

// =============================================================================
// 🌍 VARIABLES GLOBALES
// =============================================================================
// Definir conocimientoData globalmente
if (typeof window.conocimientoData === 'undefined') {
    window.conocimientoData = [];
    console.log('✅ conocimientoData inicializada');
} else {
    console.log('⚠️ conocimientoData ya existía');
}
let conocimientoData = window.conocimientoData;

// =============================================================================
// 🔧 FUNCIONES DE UTILIDAD
// =============================================================================

/**
 * Mostrar toast con fallback a alert
 */
function mostrarToast(mensaje, tipo = 'info') {
    if (typeof window.showToast === 'function') {
        window.showToast(mensaje, tipo);
    } else {
        console.log(`${tipo.toUpperCase()}: ${mensaje}`);
        // Fallback a alert solo para errores críticos
        if (tipo === 'error') {
            alert(`Error: ${mensaje}`);
        }
    }
}

// Exportar inmediatamente
window.mostrarToast = mostrarToast;
console.log('✅ mostrarToast exportada:', typeof window.mostrarToast);
console.log('🔍 mostrarToast en window:', window.hasOwnProperty('mostrarToast'));


async function cargarConocimiento() {
    console.log('🚀 INICIANDO cargarConocimiento...');
    console.log('🔍 window disponible:', typeof window !== 'undefined');
    console.log('🔍 PANEL_CONFIG existe:', !!window.PANEL_CONFIG);
    
    try {
        // Verificar que PANEL_CONFIG esté disponible
        if (!window.PANEL_CONFIG || !window.PANEL_CONFIG.endpoints || !window.PANEL_CONFIG.endpoints.bloques) {
            console.error('❌ PANEL_CONFIG no está configurado correctamente');
            console.log('🔍 window.PANEL_CONFIG:', window.PANEL_CONFIG);
            
            // Usar función showToast si está disponible
            if (typeof window.showToast === 'function') {
                mostrarToast('Error de configuración del panel', 'error');
            } else {
                console.error('❌ showToast no está disponible');
                alert('Error de configuración del panel');
            }
            return;
        }

        const endpoint = window.PANEL_CONFIG.endpoints.bloques;
        console.log('🔄 Cargando conocimiento desde:', endpoint);

        const response = await fetch(endpoint, {
            method: 'GET',
            credentials: 'same-origin', // Incluir cookies de sesión
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Marcar como AJAX
            }
        });
        console.log('📡 Response status:', response.status, response.statusText);
        console.log('📡 Response headers:', [...response.headers.entries()]);
        
        // Si es 401, significa que la sesión expiró
        if (response.status === 401) {
            console.error('❌ Sesión expirada o no autenticado');
            const errorData = await response.json();
            console.error('🔐 Error de auth:', errorData);
            if (errorData.error === 'authentication_required') {
                // Mostrar mensaje de error específico para sesión expirada
                mostrarBannerSesionExpirada();
                throw new Error(`Sesión expirada. Por favor, recarga la página e inicia sesión nuevamente.`);
            }
        }
        
        // Si es una redirección (302), significa que no estamos autenticados
        if (response.status === 302) {
            console.error('❌ Redirección detectada - posible problema de sesión');
            throw new Error(`Redirección detectada (${response.status}) - problema de autenticación`);
        }
        
        // Si no es JSON, podría ser una página HTML de error
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('❌ Respuesta no es JSON:', contentType);
            const textResponse = await response.text();
            console.error('📄 Contenido de respuesta:', textResponse.substring(0, 500));
            throw new Error(`Respuesta no es JSON (${contentType})`);
        }

        const resultado = await response.json();
        console.log('📦 Resultado JSON:', resultado);

        if (!response.ok || !resultado.success) {
            throw new Error(resultado.message || "Error cargando conocimiento");
        }

        conocimientoData = resultado.data;
        console.log(`✅ Cargados ${conocimientoData.length} bloques de conocimiento desde el servidor`);
        
        actualizarEstadisticas();
        mostrarConocimiento(conocimientoData);
        actualizarFiltroEtiquetas();
        ocultarBannerDebug();
        
    } catch (error) {
        console.error("❌ Error completo al cargar conocimiento:", error);
        console.warn("⚠️ Fallback a demo por error:", error.message);
        mostrarBannerDemo(error.message);
        usarDatosDemo();
    }
}

// Exportar inmediatamente
window.cargarConocimiento = cargarConocimiento;
console.log('✅ cargarConocimiento exportada:', typeof window.cargarConocimiento);
console.log('🔍 cargarConocimiento en window:', window.hasOwnProperty('cargarConocimiento'));



/**
 * Actualizar estadísticas de bloques
 */
function actualizarEstadisticas() {
    const totalBloques = conocimientoData.length;
    const totalEtiquetas = new Set(conocimientoData.flatMap(b => b.etiquetas || [])).size;
    const bloquesPrioritarios = conocimientoData.filter(b => b.prioridad).length;
    
    const totalBloquesEl = document.getElementById('total-bloques');
    const totalEtiquetasEl = document.getElementById('total-etiquetas');
    const bloquesPrioritariosEl = document.getElementById('bloques-prioritarios');
    
    if (totalBloquesEl) totalBloquesEl.textContent = totalBloques;
    if (totalEtiquetasEl) totalEtiquetasEl.textContent = totalEtiquetas;
    if (bloquesPrioritariosEl) bloquesPrioritariosEl.textContent = bloquesPrioritarios;
}

/**
 * Mostrar bloques de conocimiento en el DOM
 */
function mostrarConocimiento(bloques) {
    const container = document.getElementById('lista-conocimiento');
    if (!container) return;
    
    if (bloques.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="text-6xl mb-4">📚</div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No hay bloques de conocimiento</h3>
                <p class="text-gray-500 mb-4">Comienza agregando el primer bloque de conocimiento para entrenar a ${window.PANEL_CONFIG.nombreNora}</p>
                <button onclick="switchTab('agregar-conocimiento')" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-teal-600 hover:bg-teal-700">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    Agregar Primer Bloque
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = bloques.map(bloque => crearElementoBloque(bloque)).join('');
}

/**
 * Crear elemento HTML para un bloque
 */
function crearElementoBloque(bloque) {
    const fechaFormateada = formatDate(bloque.fecha_creacion);
    const etiquetasHtml = (bloque.etiquetas || []).map(etiqueta => 
        `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">${escapeHtml(etiqueta)}</span>`
    ).join('');
    
    const prioridadBadge = bloque.prioridad ? 
        `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd"></path>
            </svg>
            Prioritario
        </span>` : '';
    
    return `
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200" data-bloque-id="${bloque.id}">
            <div class="flex justify-between items-start mb-3">
                <div class="flex items-center space-x-2">
                    ${prioridadBadge}
                    <span class="text-xs text-gray-500">${fechaFormateada}</span>
                </div>
                <div class="flex items-center space-x-2">
                    <button onclick="editarBloque('${bloque.id}')" class="text-gray-400 hover:text-blue-600 transition-colors duration-200">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                    <button onclick="eliminarBloque('${bloque.id}')" class="text-gray-400 hover:text-red-600 transition-colors duration-200">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="mb-3">
                <p class="text-gray-800 text-sm leading-relaxed">${escapeHtml(bloque.contenido)}</p>
            </div>
            
            ${etiquetasHtml ? `<div class="flex flex-wrap gap-1">${etiquetasHtml}</div>` : ''}
        </div>
    `;
}

/**
 * Agregar nuevo bloque de conocimiento
 */
async function agregarBloque() {
    const contenido = document.getElementById('nuevo-contenido');
    const etiquetasInput = document.getElementById('nuevas-etiquetas');
    const prioridadCheck = document.getElementById('nueva-prioridad');
    const submitBtn = document.getElementById('btn-agregar-conocimiento');
    
    if (!contenido || !etiquetasInput || !prioridadCheck || !submitBtn) {
        console.error('Elementos del formulario no encontrados');
        return;
    }
    
    const contenidoTexto = contenido.value.trim();
    const etiquetasTexto = etiquetasInput.value.trim();
    const esPrioritario = prioridadCheck.checked;
    
    // Validaciones
    if (!contenidoTexto) {
        mostrarToast('El contenido es obligatorio', 'error');
        contenido.focus();
        return;
    }
    
    if (contenidoTexto.length > window.PANEL_CONFIG.limits.maxContentLength) {
        mostrarToast(`El contenido no puede exceder ${window.PANEL_CONFIG.limits.maxContentLength} caracteres`, 'error');
        contenido.focus();
        return;
    }
    
    // Procesar etiquetas
    const etiquetas = etiquetasTexto ? 
        etiquetasTexto.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0) : 
        [];
    
    if (etiquetas.length > window.PANEL_CONFIG.limits.maxTags) {
        mostrarToast(`No puedes agregar más de ${window.PANEL_CONFIG.limits.maxTags} etiquetas`, 'error');
        etiquetasInput.focus();
        return;
    }
    
    // Preparar datos
    const nuevoBloque = {
        contenido: contenidoTexto,
        etiquetas: etiquetas,
        prioridad: esPrioritario
    };
    
    // Estado de carga
    setButtonLoading(submitBtn, true);
    
    try {
        const response = await fetch(window.PANEL_CONFIG.endpoints.bloques, {
            method: 'POST',
            credentials: 'same-origin', // Incluir cookies de sesión
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(nuevoBloque)
        });
        
        // Manejar error de autenticación
        if (response.status === 401) {
            const errorData = await response.json();
            if (errorData.error === 'authentication_required') {
                mostrarBannerSesionExpirada();
                throw new Error('Sesión expirada. Por favor, recarga la página e inicia sesión nuevamente.');
            }
        }
        
        const resultado = await response.json();
        
        if (resultado.success) {
            mostrarToast('✅ Bloque agregado correctamente', 'success');
            
            // Limpiar formulario
            clearForm('form-agregar-conocimiento');
            
            // Recargar conocimiento
            await cargarConocimiento();
            
            // Cambiar a tab de ver conocimiento
            switchTab('ver-conocimiento');
            
        } else {
            throw new Error(resultado.message || 'Error al agregar bloque');
        }
        
    } catch (error) {
        console.error('Error al agregar bloque:', error);
        mostrarToast(error.message || 'Error al agregar bloque', 'error');
    } finally {
        setButtonLoading(submitBtn, false);
    }
}

// Exportar inmediatamente
window.agregarBloque = agregarBloque;
console.log('✅ agregarBloque exportada:', typeof window.agregarBloque);

/**
 * Eliminar bloque de conocimiento
 */
async function eliminarBloque(idBloque) {
    if (!confirm('¿Estás seguro de que quieres eliminar este bloque de conocimiento?')) {
        return;
    }
    
    try {
        const response = await fetch(`${window.PANEL_CONFIG.endpoints.bloques}/${idBloque}`, {
            method: 'DELETE',
            credentials: 'same-origin', // Incluir cookies de sesión
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        // Manejar error de autenticación
        if (response.status === 401) {
            const errorData = await response.json();
            if (errorData.error === 'authentication_required') {
                mostrarBannerSesionExpirada();
                throw new Error('Sesión expirada. Por favor, recarga la página e inicia sesión nuevamente.');
            }
        }
        
        const resultado = await response.json();
        
        if (resultado.success) {
            mostrarToast('✅ Bloque eliminado correctamente', 'success');
            
            // Recargar conocimiento
            await cargarConocimiento();
        } else {
            throw new Error(resultado.message || 'Error al eliminar bloque');
        }
        
    } catch (error) {
        console.error('Error al eliminar bloque:', error);
        mostrarToast(error.message || 'Error al eliminar bloque', 'error');
    }
}

// Exportar inmediatamente
window.eliminarBloque = eliminarBloque;
console.log('✅ eliminarBloque exportada:', typeof window.eliminarBloque);

/**
 * Editar bloque de conocimiento (placeholder)
 */
function editarBloque(idBloque) {
    // TODO: Implementar edición de bloques
    mostrarToast('Función de edición en desarrollo', 'info');
    console.log('Editar bloque:', idBloque);
}

// Exportar inmediatamente
window.editarBloque = editarBloque;
console.log('✅ editarBloque exportada:', typeof window.editarBloque);

// =============================================================================
// 🏷️ FUNCIONES DE ETIQUETAS
// =============================================================================

/**
 * Actualizar filtro de etiquetas
 */
function actualizarFiltroEtiquetas() {
    const filtroContainer = document.getElementById('filtro-etiquetas');
    if (!filtroContainer) return;
    
    const todasLasEtiquetas = new Set();
    conocimientoData.forEach(bloque => {
        (bloque.etiquetas || []).forEach(etiqueta => todasLasEtiquetas.add(etiqueta));
    });
    
    if (todasLasEtiquetas.size === 0) {
        filtroContainer.innerHTML = '<p class="text-gray-500 text-sm">No hay etiquetas disponibles</p>';
        return;
    }
    
    const etiquetasArray = Array.from(todasLasEtiquetas).sort();
    filtroContainer.innerHTML = `
        <div class="flex flex-wrap gap-2">
            <button onclick="filtrarPorEtiqueta(null)" class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors">
                Todas
            </button>
            ${etiquetasArray.map(etiqueta => `
                <button onclick="filtrarPorEtiqueta('${escapeHtml(etiqueta)}')" class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors">
                    ${escapeHtml(etiqueta)}
                </button>
            `).join('')}
        </div>
    `;
}

/**
 * Filtrar bloques por etiqueta
 */
function filtrarPorEtiqueta(etiqueta) {
    let bloquesFiltrados;
    
    if (etiqueta === null) {
        bloquesFiltrados = conocimientoData;
    } else {
        bloquesFiltrados = conocimientoData.filter(bloque => 
            (bloque.etiquetas || []).includes(etiqueta)
        );
    }
    
    mostrarConocimiento(bloquesFiltrados);
    
    // Actualizar estado visual de filtros
    const botonesFiltro = document.querySelectorAll('#filtro-etiquetas button');
    botonesFiltro.forEach(btn => {
        btn.classList.remove('bg-blue-500', 'text-white');
        btn.classList.add('bg-blue-100', 'text-blue-700');
    });
    
    // Marcar filtro activo
    event.target.classList.remove('bg-blue-100', 'text-blue-700');
    event.target.classList.add('bg-blue-500', 'text-white');
}

/**
 * Cargar estadísticas de etiquetas
 */
function cargarEstadisticasEtiquetas() {
    // TODO: Implementar vista de estadísticas de etiquetas
    console.log('Cargando estadísticas de etiquetas...');
}

// =============================================================================
// 🧪 FUNCIONES DE DEBUGGING Y DEMO
// =============================================================================

/**
 * Mostrar banner de modo demo
 */
function mostrarBannerDemo(errorMessage = 'Servidor no disponible') {
    const bannerDemo = document.createElement('div');
    bannerDemo.id = 'banner-demo';
    bannerDemo.className = 'bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4 rounded';
    bannerDemo.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <span class="text-2xl">⚠️</span>
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">Modo Demo - Datos de Ejemplo</p>
                <p class="text-xs mt-1">No se pudo conectar al servidor (${errorMessage}). Se están mostrando datos de ejemplo para demostrar la funcionalidad.</p>
            </div>
        </div>
    `;
    
    // Eliminar banner existente si hay uno
    const bannerExistente = document.getElementById('banner-demo');
    if (bannerExistente) {
        bannerExistente.remove();
    }
    
    // Insertar al inicio del contenido principal
    const mainContent = document.querySelector('.max-w-4xl');
    if (mainContent) {
        mainContent.insertBefore(bannerDemo, mainContent.firstChild);
    }
}

/**
 * Ocultar banner de debug
 */
function ocultarBannerDebug() {
    const bannerDemo = document.getElementById('banner-demo');
    if (bannerDemo) {
        bannerDemo.remove();
    }
}

/**
 * Mostrar banner de sesión expirada
 */
function mostrarBannerSesionExpirada() {
    const bannerSesion = document.createElement('div');
    bannerSesion.id = 'banner-sesion-expirada';
    bannerSesion.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4 rounded';
    bannerSesion.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <span class="text-2xl">🔐</span>
            </div>
            <div class="ml-3 flex-grow">
                <p class="text-sm font-medium">Sesión Expirada</p>
                <p class="text-xs mt-1">Tu sesión ha expirado. Por favor, recarga la página e inicia sesión nuevamente para gestionar el conocimiento.</p>
            </div>
            <div class="ml-3">
                <button onclick="window.location.reload()" class="bg-red-600 hover:bg-red-700 text-white text-xs px-3 py-1 rounded transition-colors">
                    🔄 Recargar Página
                </button>
            </div>
        </div>
    `;
    
    // Eliminar banner existente si hay uno
    const bannerExistente = document.getElementById('banner-sesion-expirada');
    if (bannerExistente) {
        bannerExistente.remove();
    }
    
    // Insertar al inicio del contenido principal
    const mainContent = document.querySelector('.max-w-4xl');
    if (mainContent) {
        mainContent.insertBefore(bannerSesion, mainContent.firstChild);
    }
}

/**
 * Usar datos de demostración
 */
function usarDatosDemo() {
    conocimientoData = [
        {
            id: 'demo-1',
            contenido: '🏢 Somos una empresa líder en tecnología que se especializa en soluciones innovadoras.',
            etiquetas: ['empresa', 'tecnología', 'innovación'],
            fecha_creacion: new Date().toISOString(),
            prioridad: true,
            activo: true
        },
        {
            id: 'demo-2',
            contenido: '📞 Nuestro horario de atención al cliente es de lunes a viernes de 9:00 AM a 6:00 PM.',
            etiquetas: ['horario', 'atención', 'contacto'],
            fecha_creacion: new Date(Date.now() - 86400000).toISOString(),
            prioridad: false,
            activo: true
        },
        {
            id: 'demo-3',
            contenido: '🚀 Ofrecemos servicios de consultoría, desarrollo de software y soporte técnico.',
            etiquetas: ['servicios', 'consultoría', 'desarrollo'],
            fecha_creacion: new Date(Date.now() - 172800000).toISOString(),
            prioridad: false,
            activo: true
        }
    ];
    
    actualizarEstadisticas();
    mostrarConocimiento(conocimientoData);
    actualizarFiltroEtiquetas();
}

// =============================================================================
// 🌟 EXPORTAR FUNCIONES GLOBALES
// =============================================================================
console.log('🔗 Exportando funciones globales...');

// Función de inicialización para exportar después de que todo esté cargado
function inicializarConocimientoManager() {
    // Exportar funciones principales
    window.cargarConocimiento = cargarConocimiento;
    window.agregarBloque = agregarBloque;
    window.eliminarBloque = eliminarBloque;
    window.editarBloque = editarBloque;
    window.filtrarPorEtiqueta = filtrarPorEtiqueta;
    window.actualizarFiltroEtiquetas = actualizarFiltroEtiquetas;
    window.mostrarToast = mostrarToast;
    
    // Verificar exportaciones
    console.log('✅ Funciones exportadas:', {
        cargarConocimiento: typeof window.cargarConocimiento,
        agregarBloque: typeof window.agregarBloque,
        eliminarBloque: typeof window.eliminarBloque,
        editarBloque: typeof window.editarBloque,
        filtrarPorEtiqueta: typeof window.filtrarPorEtiqueta,
        actualizarFiltroEtiquetas: typeof window.actualizarFiltroEtiquetas,
        mostrarToast: typeof window.mostrarToast
    });
    
    console.log('📚 CONOCIMIENTO MANAGER completamente inicializado');
}

// Ejecutar inicialización inmediatamente
inicializarConocimientoManager();

// También exportar la función de inicialización por si se necesita llamar manualmente
window.inicializarConocimientoManager = inicializarConocimientoManager;

console.log('🎉 CONOCIMIENTO MANAGER - Archivo completamente procesado');
console.log('🔍 Funciones finales en window:', {
    cargarConocimiento: typeof window.cargarConocimiento,
    mostrarToast: typeof window.mostrarToast,
    agregarBloque: typeof window.agregarBloque,
    eliminarBloque: typeof window.eliminarBloque
});
