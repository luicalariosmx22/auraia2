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

// Bandera para evitar configuración múltiple de eventos
let eventosConfigurados = false;

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
        actualizarOpcionesDropdown(); // Actualizar dropdown
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
    console.log('🔍 mostrarConocimiento llamada con:', bloques);
    console.log('📊 Tipo de bloques:', typeof bloques);
    console.log('📊 Array?:', Array.isArray(bloques));
    console.log('📊 Longitud:', bloques ? bloques.length : 'N/A');
    
    const container = document.getElementById('lista-conocimiento');
    console.log('📊 Container encontrado:', !!container);
    
    if (!container) {
        console.error('❌ Container lista-conocimiento no encontrado');
        return;
    }
    
    if (!bloques || bloques.length === 0) {
        console.log('📋 No hay bloques, mostrando mensaje vacío');
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
    
    console.log('🔨 Creando HTML para bloques...');
    try {
        const html = bloques.map((bloque, index) => {
            console.log(`📋 Procesando bloque ${index + 1}:`, bloque);
            
            // Verificar que las funciones necesarias existan
            if (typeof window.crearElementoBloque !== 'function') {
                console.error('❌ crearElementoBloque no está disponible');
                throw new Error('crearElementoBloque no está disponible');
            }
            
            return window.crearElementoBloque(bloque);
        }).join('');
        
        console.log('✅ HTML generado, longitud:', html.length);
        console.log('📄 HTML preview:', html.substring(0, 200) + '...');
        
        container.innerHTML = html;
        console.log('✅ HTML insertado en container');
        
    } catch (error) {
        console.error('❌ Error creando HTML para bloques:', error);
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="text-6xl mb-4">❌</div>
                <h3 class="text-lg font-medium text-red-900 mb-2">Error mostrando bloques</h3>
                <p class="text-red-500 mb-4">Error: ${error.message}</p>
                <button onclick="window.location.reload()" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700">
                    🔄 Recargar Página
                </button>
            </div>
        `;
    }
}

/**
 * Crear elemento HTML para un bloque
 */
function crearElementoBloque(bloque) {
    console.log('🔨 crearElementoBloque llamada con:', bloque);
    
    try {
        // Verificar funciones necesarias
        if (typeof window.formatDate !== 'function') {
            console.error('❌ formatDate no está disponible');
            throw new Error('formatDate no está disponible');
        }
        if (typeof window.escapeHtml !== 'function') {
            console.error('❌ escapeHtml no está disponible');
            throw new Error('escapeHtml no está disponible');
        }
        
        const fechaFormateada = window.formatDate(bloque.fecha_creacion);
        console.log('📅 Fecha formateada:', fechaFormateada);
        
        const etiquetasHtml = (bloque.etiquetas || []).map(etiqueta => 
            `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">${window.escapeHtml(etiqueta)}</span>`
        ).join('');
        console.log('🏷️ Etiquetas HTML:', etiquetasHtml);
        
        const prioridadBadge = bloque.prioridad ? 
            `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd"></path>
                </svg>
                Prioritario
            </span>` : '';
        console.log('⭐ Prioridad badge:', prioridadBadge);
        
        const html = `
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
                    <p class="text-gray-800 text-sm leading-relaxed">${window.escapeHtml(bloque.contenido)}</p>
                </div>
                
                ${etiquetasHtml ? `<div class="flex flex-wrap gap-1">${etiquetasHtml}</div>` : ''}
            </div>
        `;
        
        console.log('✅ HTML creado exitosamente, longitud:', html.length);
        return html;
        
    } catch (error) {
        console.error('❌ Error en crearElementoBloque:', error);
        return `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <p class="text-red-700">Error creando bloque: ${error.message}</p>
                <pre class="text-xs text-red-600 mt-2">${JSON.stringify(bloque, null, 2)}</pre>
            </div>
        `;
    }
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
            if (typeof window.switchTab === 'function') {
                const tabButtons = document.querySelectorAll('.tab-button');
                const tabContents = document.querySelectorAll('.tab-content');
                window.switchTab('ver-conocimiento', tabButtons, tabContents);
            } else {
                console.warn('⚠️ switchTab no disponible');
            }
            
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
 * Filtrar bloques por etiqueta (MEJORADO)
 */
function filtrarPorEtiqueta(etiqueta) {
    console.log(`🏷️ Filtrando por etiqueta: "${etiqueta}"`);
    
    let bloquesFiltrados;
    
    if (etiqueta === null || etiqueta === '' || etiqueta === 'todas') {
        bloquesFiltrados = conocimientoData;
        console.log('📋 Mostrando todos los bloques');
    } else {
        bloquesFiltrados = conocimientoData.filter(bloque => {
            const etiquetas = bloque.etiquetas || [];
            
            // Búsqueda exacta
            const coincidenciaExacta = etiquetas.includes(etiqueta);
            
            // Búsqueda parcial (para etiquetas como "Curso Inteligencia Artificial")
            const coincidenciaParcial = etiquetas.some(e => 
                e.toLowerCase().includes(etiqueta.toLowerCase()) ||
                etiqueta.toLowerCase().includes(e.toLowerCase())
            );
            
            return coincidenciaExacta || coincidenciaParcial;
        });
        
        console.log(`📊 Filtrado por "${etiqueta}": ${bloquesFiltrados.length}/${conocimientoData.length} bloques`);
    }
    
    // Mostrar bloques filtrados
    mostrarConocimiento(bloquesFiltrados);
    
    // Actualizar estadísticas
    if (etiqueta === null || etiqueta === '' || etiqueta === 'todas') {
        actualizarEstadisticas();
    } else {
        actualizarEstadisticasFiltradas(bloquesFiltrados, `etiqueta: ${etiqueta}`);
    }
    
    // Actualizar estado visual de filtros
    actualizarEstadoFiltros(etiqueta);
    
    // Actualizar dropdown si existe
    const filtroEtiqueta = document.getElementById('filtro-etiqueta');
    if (filtroEtiqueta) {
        filtroEtiqueta.value = etiqueta || '';
    }
}

/**
 * Actualizar estado visual de los filtros
 */
function actualizarEstadoFiltros(etiquetaActiva) {
    const botonesFiltro = document.querySelectorAll('#filtro-etiquetas button');
    
    botonesFiltro.forEach(btn => {
        const textoBoton = btn.textContent.trim();
        
        if ((etiquetaActiva === null && textoBoton === 'Todas') || 
            textoBoton === etiquetaActiva) {
            // Botón activo
            btn.classList.remove('bg-blue-100', 'text-blue-700', 'bg-gray-100', 'text-gray-700');
            btn.classList.add('bg-blue-500', 'text-white');
        } else {
            // Botón inactivo
            btn.classList.remove('bg-blue-500', 'text-white');
            if (textoBoton === 'Todas') {
                btn.classList.add('bg-gray-100', 'text-gray-700');
            } else {
                btn.classList.add('bg-blue-100', 'text-blue-700');
            }
        }
    });
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
    window.filtrarConocimiento = filtrarConocimiento;
    window.configurarEventosConocimiento = configurarEventosConocimiento;
    window.reinicializarEventosConocimiento = reinicializarEventosConocimiento;
    
    // Exportar nuevas funciones de búsqueda mejorada
    window.limpiarBusqueda = limpiarBusqueda;
    window.busquedaAvanzada = busquedaAvanzada;
    window.mostrarTodosLosBloques = mostrarTodosLosBloques;
    window.actualizarOpcionesDropdown = actualizarOpcionesDropdown;
    window.actualizarEstadoFiltros = actualizarEstadoFiltros;
    
    // Configurar eventos si el DOM está listo (solo una vez)
    if (!eventosConfigurados) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', configurarEventosConocimiento);
        } else {
            configurarEventosConocimiento();
        }
    } else {
        console.log('⚠️ Eventos ya configurados, saltando configuración');
    }
    
    // Verificar exportaciones
    console.log('✅ Funciones exportadas:', {
        cargarConocimiento: typeof window.cargarConocimiento,
        agregarBloque: typeof window.agregarBloque,
        eliminarBloque: typeof window.eliminarBloque,
        editarBloque: typeof window.editarBloque,
        filtrarPorEtiqueta: typeof window.filtrarPorEtiqueta,
        actualizarFiltroEtiquetas: typeof window.actualizarFiltroEtiquetas,
        mostrarToast: typeof window.mostrarToast,
        filtrarConocimiento: typeof window.filtrarConocimiento,
        configurarEventosConocimiento: typeof window.configurarEventosConocimiento,
        reinicializarEventosConocimiento: typeof window.reinicializarEventosConocimiento
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

// Exportar funciones necesarias globalmente
window.crearElementoBloque = crearElementoBloque;
window.mostrarConocimiento = mostrarConocimiento;
console.log('✅ crearElementoBloque exportada:', typeof window.crearElementoBloque);
console.log('✅ mostrarConocimiento exportada:', typeof window.mostrarConocimiento);

// =============================================================================
// 🎯 CONFIGURACIÓN DE EVENTOS
// =============================================================================

/**
 * Configurar eventos del formulario de conocimiento
 */
function configurarEventosConocimiento() {
    // Evitar configuración múltiple
    if (eventosConfigurados) {
        console.log('⚠️ Eventos ya configurados, saltando...');
        return;
    }
    
    console.log('🎯 Configurando eventos de conocimiento...');
    
    // Configurar formulario de agregar conocimiento
    const formAgregar = document.getElementById('form-agregar-conocimiento');
    if (formAgregar) {
        // Prevenir submit por defecto y usar nuestra función
        formAgregar.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('📝 Submit del formulario interceptado');
            agregarBloque();
        });
        console.log('✅ Evento submit configurado para form-agregar-conocimiento');
    } else {
        console.warn('⚠️ Formulario form-agregar-conocimiento no encontrado');
    }
    
    // Configurar contador de caracteres
    const contenidoTextarea = document.getElementById('nuevo-contenido');
    const contadorCaracteres = document.getElementById('contador-caracteres');
    if (contenidoTextarea && contadorCaracteres) {
        contenidoTextarea.addEventListener('input', function() {
            const length = this.value.length;
            contadorCaracteres.textContent = length;
            
            // Cambiar color según el límite
            if (length > 450) {
                contadorCaracteres.className = 'text-red-500 font-medium';
            } else if (length > 400) {
                contadorCaracteres.className = 'text-yellow-500 font-medium';
            } else {
                contadorCaracteres.className = 'text-gray-500';
            }
        });
        console.log('✅ Contador de caracteres configurado');
    }
    
    // Configurar búsqueda de conocimiento (MEJORADO)
    const buscarInput = document.getElementById('buscar-conocimiento');
    if (buscarInput) {
        // Búsqueda en tiempo real con debounce
        let timeoutBusqueda;
        
        buscarInput.addEventListener('input', function() {
            const termino = this.value.toLowerCase().trim();
            
            // Limpiar timeout anterior
            clearTimeout(timeoutBusqueda);
            
            // Aplicar debounce de 300ms para evitar búsquedas excesivas
            timeoutBusqueda = setTimeout(() => {
                console.log(`🔍 Buscando: "${termino}"`);
                filtrarConocimiento(termino);
            }, 300);
        });
        
        // Manejar tecla Enter para búsqueda avanzada
        buscarInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const termino = this.value.toLowerCase().trim();
                if (termino) {
                    console.log('🔬 Activando búsqueda avanzada');
                    const resultados = busquedaAvanzada(termino);
                    mostrarConocimiento(resultados);
                    actualizarEstadisticasFiltradas(resultados, termino);
                }
            }
            
            // Limpiar con Escape
            if (e.key === 'Escape') {
                this.value = '';
                limpiarBusqueda();
            }
        });
        
        // Agregar placeholder dinámico con sugerencias
        const sugerencias = [
            '🔍 Buscar "curso inteligencia artificial"...',
            '🔍 Buscar "presencial"...',
            '🔍 Buscar "duración"...',
            '🔍 Buscar "costo"...',
            '🔍 Buscar en el conocimiento...'
        ];
        
        let indiceSugerencia = 0;
        setInterval(() => {
            if (buscarInput.value === '') {
                buscarInput.placeholder = sugerencias[indiceSugerencia];
                indiceSugerencia = (indiceSugerencia + 1) % sugerencias.length;
            }
        }, 3000);
        
        console.log('✅ Búsqueda de conocimiento mejorada configurada');
    }
    
    // Configurar filtro de etiquetas (MEJORADO)
    const filtroEtiqueta = document.getElementById('filtro-etiqueta');
    if (filtroEtiqueta) {
        filtroEtiqueta.addEventListener('change', function() {
            const etiqueta = this.value;
            console.log(`🏷️ Filtro dropdown cambiado a: "${etiqueta}"`);
            
            // Limpiar búsqueda de texto al cambiar filtro
            const buscarInput = document.getElementById('buscar-conocimiento');
            if (buscarInput && buscarInput.value.trim() !== '') {
                buscarInput.value = '';
                console.log('🧹 Búsqueda de texto limpiada al cambiar filtro');
            }
            
            filtrarPorEtiqueta(etiqueta);
        });
        console.log('✅ Filtro de etiquetas mejorado configurado');
    }
    
    // Actualizar opciones del dropdown con las etiquetas disponibles
    actualizarOpcionesDropdown();
    
    // Marcar eventos como configurados
    eventosConfigurados = true;
    console.log('✅ Todos los eventos configurados correctamente');
}

/**
 * Reinicializar eventos (útil para debugging)
 */
function reinicializarEventosConocimiento() {
    console.log('🔄 Reinicializando eventos de conocimiento...');
    eventosConfigurados = false;
    configurarEventosConocimiento();
}

// =============================================================================
// 🔍 FUNCIONES DE FILTRADO Y BÚSQUEDA
// =============================================================================

/**
 * Filtrar conocimiento por término de búsqueda (MEJORADO)
 */
function filtrarConocimiento(termino) {
    console.log(`🔍 Filtrando conocimiento por: "${termino}"`);
    
    const terminoLower = termino.toLowerCase().trim();
    
    // Si no hay término, mostrar todos los bloques
    if (terminoLower === '') {
        mostrarTodosLosBloques();
        return;
    }
    
    // Buscar en los datos originales (más eficiente)
    const bloquesFiltrados = conocimientoData.filter(bloque => {
        // Buscar en contenido
        const contenido = (bloque.contenido || '').toLowerCase();
        const coincideContenido = contenido.includes(terminoLower);
        
        // Buscar en etiquetas
        const etiquetas = bloque.etiquetas || [];
        const coincideEtiquetas = etiquetas.some(etiqueta => 
            etiqueta.toLowerCase().includes(terminoLower)
        );
        
        // Buscar términos específicos de IA
        const terminosIA = ['inteligencia artificial', 'curso ia', 'artificial', 'inteligencia'];
        const coincideIA = terminosIA.some(terminoIA => 
            terminoLower.includes(terminoIA) && (
                coincideContenido || coincideEtiquetas
            )
        );
        
        return coincideContenido || coincideEtiquetas || coincideIA;
    });
    
    console.log(`📊 Resultados de búsqueda: ${bloquesFiltrados.length}/${conocimientoData.length}`);
    
    // Mostrar bloques filtrados
    mostrarConocimiento(bloquesFiltrados);
    
    // Actualizar estadísticas con los resultados filtrados
    actualizarEstadisticasFiltradas(bloquesFiltrados, termino);
}

/**
 * Mostrar todos los bloques (sin filtro)
 */
function mostrarTodosLosBloques() {
    console.log('📋 Mostrando todos los bloques');
    mostrarConocimiento(conocimientoData);
    
    // Restaurar estadísticas completas
    actualizarEstadisticas();
    
    // Eliminar mensaje de no resultados si existe
    const mensajeNoResultados = document.getElementById('mensaje-no-resultados');
    if (mensajeNoResultados) {
        mensajeNoResultados.remove();
    }
}

/**
 * Actualizar estadísticas para resultados filtrados
 */
function actualizarEstadisticasFiltradas(bloquesFiltrados, termino) {
    const totalBloques = bloquesFiltrados.length;
    const totalEtiquetas = new Set(bloquesFiltrados.flatMap(b => b.etiquetas || [])).size;
    const bloquesPrioritarios = bloquesFiltrados.filter(b => b.prioridad).length;
    
    // Actualizar elementos de estadísticas
    const totalBloquesEl = document.getElementById('total-bloques');
    const totalEtiquetasEl = document.getElementById('total-etiquetas');
    
    if (totalBloquesEl) {
        totalBloquesEl.textContent = `${totalBloques} (filtrados)`;
    }
    if (totalEtiquetasEl) {
        totalEtiquetasEl.textContent = totalEtiquetas;
    }
    
    // Mostrar mensaje de filtrado
    mostrarMensajeFiltrado(totalBloques, termino);
}

/**
 * Mostrar mensaje de filtrado
 */
function mostrarMensajeFiltrado(totalResultados, termino) {
    const container = document.getElementById('conocimiento-list');
    if (!container) return;
    
    // Eliminar mensaje anterior si existe
    const mensajeAnterior = document.getElementById('mensaje-filtrado');
    if (mensajeAnterior) {
        mensajeAnterior.remove();
    }
    
    // Crear nuevo mensaje
    const mensajeFiltrado = document.createElement('div');
    mensajeFiltrado.id = 'mensaje-filtrado';
    mensajeFiltrado.className = 'mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg';
    
    if (totalResultados === 0) {
        mensajeFiltrado.innerHTML = `
            <div class="flex items-center text-blue-800">
                <span class="text-2xl mr-2">🔍</span>
                <div>
                    <p class="font-medium">No se encontraron resultados para "${termino}"</p>
                    <p class="text-sm text-blue-600 mt-1">
                        Intenta con términos como: "curso", "inteligencia artificial", "presencial", etc.
                    </p>
                    <button onclick="limpiarBusqueda()" class="text-blue-600 hover:text-blue-800 text-sm underline mt-1">
                        Limpiar búsqueda
                    </button>
                </div>
            </div>
        `;
    } else {
        mensajeFiltrado.innerHTML = `
            <div class="flex items-center justify-between text-blue-800">
                <div class="flex items-center">
                    <span class="text-lg mr-2">�</span>
                    <span>Mostrando ${totalResultados} resultado${totalResultados !== 1 ? 's' : ''} para "${termino}"</span>
                </div>
                <button onclick="limpiarBusqueda()" class="text-blue-600 hover:text-blue-800 text-sm underline">
                    Ver todos
                </button>
            </div>
        `;
    }
    
    // Insertar al inicio del container
    container.insertBefore(mensajeFiltrado, container.firstChild);
}

/**
 * Limpiar búsqueda y mostrar todos los bloques
 */
function limpiarBusqueda() {
    console.log('🧹 Limpiando búsqueda');
    
    // Limpiar input de búsqueda
    const buscarInput = document.getElementById('buscar-conocimiento');
    if (buscarInput) {
        buscarInput.value = '';
    }
    
    // Limpiar filtro de etiquetas
    const filtroEtiqueta = document.getElementById('filtro-etiqueta');
    if (filtroEtiqueta) {
        filtroEtiqueta.value = '';
    }
    
    // Mostrar todos los bloques
    mostrarTodosLosBloques();
}

/**
 * Búsqueda avanzada con múltiples criterios
 */
function busquedaAvanzada(termino) {
    console.log(`🔬 Búsqueda avanzada: "${termino}"`);
    
    const terminoLower = termino.toLowerCase().trim();
    
    // Diferentes tipos de búsqueda
    const resultados = {
        exacta: [],
        contenido: [],
        etiquetas: [],
        parcial: []
    };
    
    conocimientoData.forEach(bloque => {
        const contenido = (bloque.contenido || '').toLowerCase();
        const etiquetas = (bloque.etiquetas || []).map(e => e.toLowerCase());
        const etiquetasTexto = etiquetas.join(' ');
        
        // Búsqueda exacta en etiquetas
        if (etiquetas.some(e => e === terminoLower)) {
            resultados.exacta.push({ ...bloque, relevancia: 100 });
        }
        // Búsqueda en contenido
        else if (contenido.includes(terminoLower)) {
            const relevancia = calcularRelevancia(contenido, terminoLower);
            resultados.contenido.push({ ...bloque, relevancia });
        }
        // Búsqueda en etiquetas (parcial)
        else if (etiquetasTexto.includes(terminoLower)) {
            resultados.etiquetas.push({ ...bloque, relevancia: 80 });
        }
        // Búsqueda parcial (palabras separadas)
        else {
            const palabras = terminoLower.split(' ');
            const coincidencias = palabras.filter(palabra => 
                contenido.includes(palabra) || etiquetasTexto.includes(palabra)
            );
            
            if (coincidencias.length > 0) {
                const relevancia = (coincidencias.length / palabras.length) * 60;
                resultados.parcial.push({ ...bloque, relevancia });
            }
        }
    });
    
    // Combinar y ordenar resultados por relevancia
    const todosResultados = [
        ...resultados.exacta,
        ...resultados.contenido.sort((a, b) => b.relevancia - a.relevancia),
        ...resultados.etiquetas,
        ...resultados.parcial.sort((a, b) => b.relevancia - a.relevancia)
    ];
    
    // Eliminar duplicados
    const resultadosUnicos = todosResultados.filter((bloque, index, arr) => 
        arr.findIndex(b => b.id === bloque.id) === index
    );
    
    console.log(`🎯 Búsqueda avanzada completada: ${resultadosUnicos.length} resultados`);
    return resultadosUnicos;
}

/**
 * Calcular relevancia de un término en el contenido
 */
function calcularRelevancia(contenido, termino) {
    const apariciones = (contenido.match(new RegExp(termino, 'g')) || []).length;
    const longitudContenido = contenido.length;
    const longitudTermino = termino.length;
    
    // Fórmula de relevancia basada en frecuencia y longitud
    return Math.min(90, (apariciones * longitudTermino * 100) / longitudContenido);
}

// Ejecutar configuración de eventos al cargar
configurarEventosConocimiento();

console.log('🎉 CONOCIMIENTO MANAGER - Archivo completamente procesado con eventos');

/**
 * Actualizar opciones del dropdown de filtros
 */
function actualizarOpcionesDropdown() {
    const filtroEtiqueta = document.getElementById('filtro-etiqueta');
    if (!filtroEtiqueta) return;
    
    // Obtener todas las etiquetas únicas
    const todasLasEtiquetas = new Set();
    conocimientoData.forEach(bloque => {
        (bloque.etiquetas || []).forEach(etiqueta => todasLasEtiquetas.add(etiqueta));
    });
    
    // Ordenar etiquetas
    const etiquetasOrdenadas = Array.from(todasLasEtiquetas).sort();
    
    // Crear opciones HTML
    let opcionesHTML = '<option value="">📋 Todas las etiquetas</option>';
    
    etiquetasOrdenadas.forEach(etiqueta => {
        // Agregar emoji especial para etiquetas de IA
        let emoji = '🏷️';
        if (etiqueta.toLowerCase().includes('inteligencia') || etiqueta.toLowerCase().includes('artificial')) {
            emoji = '🤖';
        } else if (etiqueta.toLowerCase().includes('curso')) {
            emoji = '📚';
        } else if (etiqueta.toLowerCase().includes('aura')) {
            emoji = '🌟';
        }
        
        opcionesHTML += `<option value="${escapeHtml(etiqueta)}">${emoji} ${escapeHtml(etiqueta)}</option>`;
    });
    
    filtroEtiqueta.innerHTML = opcionesHTML;
    console.log(`✅ Dropdown actualizado con ${etiquetasOrdenadas.length} etiquetas`);
}
