/**
 * 🌍 PANEL ENTRENAMIENTO - Variables Globales y Configuración Principal
 * Este archivo contiene las variables globales y configuración base para el panel de entrenamiento
 */

// =============================================================================
// 🌍 VARIABLES GLOBALES
// =============================================================================
let conocimientoData = [];

// Estado del panel
const PANEL_STATE = {
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
            
            PANEL_STATE.currentTab = targetTab;
            console.log('✅ Tab cambiada a:', targetTab);
        });
    });
    
    console.log('✅ Tabs inicializadas correctamente');
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
        }
    } catch (error) {
        console.error('❌ Error inicializando form handlers:', error);
    }
    
    try {
        if (typeof cargarConocimiento === 'function') {
            cargarConocimiento();
            console.log('✅ Conocimiento cargado');
        }
    } catch (error) {
        console.error('❌ Error cargando conocimiento:', error);
    }
    
    try {
        if (typeof initializeCharacterCounters === 'function') {
            initializeCharacterCounters();
            console.log('✅ Contadores de caracteres inicializados');
        }
    } catch (error) {
        console.error('❌ Error inicializando contadores:', error);
    }
    
    console.log('✅ Panel inicializado completamente');
});
        console.log('✅ initializeFormHandlers disponible');
        initializeFormHandlers();
    } else {
        console.error('❌ initializeFormHandlers no está definida');
    }
    
    if (typeof initializeCharacterCounters === 'function') {
        console.log('✅ initializeCharacterCounters disponible');
        initializeCharacterCounters();
    } else {
        console.warn('⚠️ initializeCharacterCounters no está definida');
    }
    
    // Cargar datos iniciales
    if (typeof cargarConocimiento === 'function') {
        console.log('✅ cargarConocimiento disponible');
        cargarConocimiento();
    } else {
        console.error('❌ cargarConocimiento no está definida');
    }
    
    // Verificar que las funciones globales estén disponibles
    if (typeof scrollToSection === 'function') {
        console.log('✅ scrollToSection disponible');
    } else {
        console.error('❌ scrollToSection no está definida');
    }
    
    if (typeof toggleExamples === 'function') {
        console.log('✅ toggleExamples disponible');
    } else {
        console.error('❌ toggleExamples no está definida');
    }
    
    console.log('✅ Panel de entrenamiento inicializado correctamente');
});

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
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 5000);
}

function getToastClasses(type) {
    const classes = {
        success: 'bg-green-100 border-green-400 text-green-700',
        error: 'bg-red-100 border-red-400 text-red-700',
        warning: 'bg-yellow-100 border-yellow-400 text-yellow-700',
        info: 'bg-blue-100 border-blue-400 text-blue-700'
    };
    return classes[type] || classes.info;
}

function getToastIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return `<span class="text-lg">${icons[type] || icons.info}</span>`;
}

/**
 * Formatear fecha para mostrar
 */
function formatDate(dateString) {
    if (!dateString) return 'Fecha no disponible';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Fecha inválida';
    }
}

/**
 * Escapar HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
