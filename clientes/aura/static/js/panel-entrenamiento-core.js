/**
 * 🌍 PANEL ENTRENAMIENTO - Variables Globales y Configuración Principal
 * Este archivo contiene las variables globales y configuración base para el panel de entrenamiento
 */

// =============================================================================
// 🌍 VARIABLES GLOBALES
// =============================================================================
let conocimientoData = [];

// Estado del panel
window.PANEL_STATE = {
    currentTab: 'ver-conocimiento',
    isLoading: false,
    unsavedChanges: false
};

// =============================================================================
// 🎯 FUNCIONES DE INICIALIZACIÓN DE TABS
// =============================================================================
function initializeTabs() {
    console.log('📑 Inicializando tabs...');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabButtons.length === 0) {
        console.warn('⚠️ No se encontraron botones de tab');
        return;
    }
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Desactivar todos los botones
            tabButtons.forEach(btn => {
                btn.classList.remove('active', 'border-teal-500', 'text-teal-600');
                btn.classList.add('border-transparent', 'text-gray-500');
            });
            
            // Activar botón actual
            button.classList.remove('border-transparent', 'text-gray-500');
            button.classList.add('active', 'border-teal-500', 'text-teal-600');
            
            // Ocultar todos los contenidos
            tabContents.forEach(content => {
                content.classList.add('hidden');
            });
            
            // Mostrar contenido objetivo
            const targetContent = document.getElementById('tab-' + targetTab);
            if (targetContent) {
                targetContent.classList.remove('hidden');
            }
            
            window.PANEL_STATE.currentTab = targetTab;
            console.log('✅ Tab cambiada a:', targetTab);
        });
    });
    
    console.log('✅ Tabs inicializadas correctamente:', tabButtons.length, 'tabs encontrados');
}

// =============================================================================
// 🔧 FUNCIONES DE UTILIDAD GLOBALES
// =============================================================================

/**
 * Mostrar notificación toast
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 ${getToastClasses(type)}`;
    toast.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                ${getToastIcon(type)}
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">${message}</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function getToastClasses(type) {
    switch (type) {
        case 'success':
            return 'bg-green-100 border border-green-400 text-green-700';
        case 'error':
            return 'bg-red-100 border border-red-400 text-red-700';
        case 'warning':
            return 'bg-yellow-100 border border-yellow-400 text-yellow-700';
        default:
            return 'bg-blue-100 border border-blue-400 text-blue-700';
    }
}

function getToastIcon(type) {
    switch (type) {
        case 'success':
            return '✅';
        case 'error':
            return '❌';
        case 'warning':
            return '⚠️';
        default:
            return 'ℹ️';
    }
}

// =============================================================================
// 🚀 INICIALIZACIÓN DEL PANEL
// =============================================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando panel de entrenamiento...');
    
    // Merge configuration from window.PANEL_CONFIG (set by template)
    if (window.PANEL_CONFIG) {
        console.log('📋 Configuración recibida del template:', window.PANEL_CONFIG);
    }
    
    // Inicializar componentes
    try {
        initializeTabs();
        console.log('✅ Tabs inicializadas');
    } catch (error) {
        console.error('❌ Error inicializando tabs:', error);
    }
    
    try {
        if (typeof initializeFormHandlers === 'function') {
            initializeFormHandlers();
            console.log('✅ Form handlers inicializados');
        } else {
            console.warn('⚠️ initializeFormHandlers no disponible');
        }
    } catch (error) {
        console.error('❌ Error inicializando form handlers:', error);
    }
    
    try {
        if (typeof cargarConocimiento === 'function') {
            cargarConocimiento();
            console.log('✅ Conocimiento cargado');
        } else {
            console.warn('⚠️ cargarConocimiento no disponible');
        }
    } catch (error) {
        console.error('❌ Error cargando conocimiento:', error);
    }
    
    try {
        if (typeof initializeCharacterCounters === 'function') {
            initializeCharacterCounters();
            console.log('✅ Contadores de caracteres inicializados');
        } else {
            console.warn('⚠️ initializeCharacterCounters no disponible');
        }
    } catch (error) {
        console.error('❌ Error inicializando contadores:', error);
    }
    
    // Verificar que las funciones globales estén disponibles
    if (typeof scrollToSection === 'function') {
        console.log('✅ scrollToSection disponible');
    } else {
        console.warn('⚠️ scrollToSection no disponible');
    }
    
    if (typeof toggleExamples === 'function') {
        console.log('✅ toggleExamples disponible');
    } else {
        console.warn('⚠️ toggleExamples no disponible');
    }
    
    console.log('✅ Panel inicializado completamente');
});

// =============================================================================
// 🌟 FUNCIONES GLOBALES DISPONIBLES
// =============================================================================
window.showToast = showToast;
window.initializeTabs = initializeTabs;
