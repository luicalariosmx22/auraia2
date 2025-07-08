/**
 * 🎨 UI UTILS - Utilidades de Interfaz de Usuario
 * Funciones para manejo de tabs, scroll, animaciones y otros elementos de UI
 */

// =============================================================================
// � ESTADO GLOBAL
// =============================================================================
if (typeof window.PANEL_STATE === 'undefined') {
    window.PANEL_STATE = {
        currentTab: 'ver-conocimiento',
        initialized: false
    };
}

// =============================================================================
// �🎯 FUNCIONES DE NAVEGACIÓN Y SCROLL
// =============================================================================

/**
 * Scroll suave a una sección específica
 */
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
        
        // Agregar efecto visual temporal
        element.classList.add('ring-4', 'ring-blue-300', 'ring-opacity-50');
        setTimeout(() => {
            element.classList.remove('ring-4', 'ring-blue-300', 'ring-opacity-50');
        }, 2000);
    }
}

/**
 * Toggle de ejemplos con animación
 */
function toggleExamples() {
    const container = document.getElementById('examples-container');
    const arrow = document.getElementById('example-arrow');
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        arrow.style.transform = 'rotate(180deg)';
    } else {
        container.classList.add('hidden');
        arrow.style.transform = 'rotate(0deg)';
    }
}

// =============================================================================
// 📑 SISTEMA DE TABS
// =============================================================================

/**
 * Inicializar sistema de tabs
 */
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            switchTab(targetTab, tabButtons, tabContents);
        });
    });
}

/**
 * Cambiar a una tab específica
 */
function switchTab(targetTab, tabButtons, tabContents) {
    // Activar botón de pestaña
    tabButtons.forEach(btn => {
        btn.classList.remove('active', 'border-teal-500', 'text-teal-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    
    const activeButton = document.querySelector(`[data-tab="${targetTab}"]`);
    if (activeButton) {
        activeButton.classList.remove('border-transparent', 'text-gray-500');
        activeButton.classList.add('active', 'border-teal-500', 'text-teal-600');
    }

    // Mostrar contenido de pestaña correspondiente
    tabContents.forEach(content => {
        content.classList.add('hidden');
    });
    
    const targetContent = document.getElementById('tab-' + targetTab);
    if (targetContent) {
        targetContent.classList.remove('hidden');
    }
    
    // Actualizar estado global
    window.PANEL_STATE.currentTab = targetTab;
    
    // Cargar datos según la pestaña
    handleTabSwitch(targetTab);
}

/**
 * Manejar cambios de tab y cargar datos necesarios
 */
function handleTabSwitch(tabName) {
    console.log(`🎯 Cambiando a pestaña: ${tabName}`);
    
    switch(tabName) {
        case 'ver-conocimiento':
            if (typeof window.cargarConocimiento === 'function') {
                window.cargarConocimiento();
            }
            break;
        case 'agregar-conocimiento':
            // Enfocar en el primer campo del formulario
            setTimeout(() => {
                const contenidoField = document.getElementById('nuevo-contenido');
                if (contenidoField) {
                    contenidoField.focus();
                }
            }, 100);
            break;
        case 'gestionar-etiquetas':
            if (typeof window.cargarEstadisticasEtiquetas === 'function') {
                window.cargarEstadisticasEtiquetas();
            }
            break;
        default:
            console.log(`Tab cargada: ${tabName}`);
    }
}

// =============================================================================
// 📊 CONTADORES DE CARACTERES
// =============================================================================

/**
 * Inicializar contadores de caracteres en formularios
 */
function initializeCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[data-max-length]');
    
    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('data-max-length'));
        const counterId = textarea.getAttribute('data-counter');
        
        if (counterId) {
            const counter = document.getElementById(counterId);
            if (counter) {
                updateCharacterCounter(textarea, counter, maxLength);
                
                textarea.addEventListener('input', () => {
                    updateCharacterCounter(textarea, counter, maxLength);
                });
            }
        }
    });
}

/**
 * Actualizar contador de caracteres
 */
function updateCharacterCounter(textarea, counter, maxLength) {
    const currentLength = textarea.value.length;
    const remaining = maxLength - currentLength;
    
    counter.textContent = `${currentLength}/${maxLength}`;
    
    // Cambiar color según proximidad al límite
    if (remaining < 50) {
        counter.className = 'text-red-500 text-sm';
    } else if (remaining < 100) {
        counter.className = 'text-yellow-500 text-sm';
    } else {
        counter.className = 'text-gray-500 text-sm';
    }
}

// =============================================================================
// 🎭 ANIMACIONES Y EFECTOS VISUALES
// =============================================================================

/**
 * Animar elemento con pulso
 */
function pulseElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('animate-pulse');
        setTimeout(() => {
            element.classList.remove('animate-pulse');
        }, 1000);
    }
}

/**
 * Efecto de carga en botón
 */
function setButtonLoading(button, isLoading = true) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = `
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Cargando...
        `;
    } else {
        button.disabled = false;
        // Restaurar texto original (debería guardarse antes)
    }
}

/**
 * Mostrar/ocultar elemento con animación fade
 */
function fadeToggle(elementId, show = null) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const isVisible = !element.classList.contains('hidden');
    const shouldShow = show !== null ? show : !isVisible;
    
    if (shouldShow && element.classList.contains('hidden')) {
        element.classList.remove('hidden');
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    } else if (!shouldShow && !element.classList.contains('hidden')) {
        element.style.opacity = '0';
        setTimeout(() => {
            element.classList.add('hidden');
        }, 300);
    }
}

// =============================================================================
// 🔄 UTILIDADES DE FORMULARIO
// =============================================================================

/**
 * Limpiar formulario
 */
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        
        // Limpiar contadores de caracteres
        const counters = form.querySelectorAll('[data-counter]');
        counters.forEach(counter => {
            const counterId = counter.getAttribute('data-counter');
            const counterElement = document.getElementById(counterId);
            if (counterElement) {
                counterElement.textContent = '0/500'; // Default
            }
        });
    }
}

// =============================================================================
// 🛡️ UTILIDADES DE SEGURIDAD Y FORMATO
// =============================================================================

/**
 * Escape HTML para prevenir XSS
 */
function escapeHtml(text) {
    if (typeof text !== 'string') {
        return text;
    }
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Formatear fecha a formato legible
 */
function formatDate(dateString) {
    if (!dateString) return 'Fecha no disponible';
    
    try {
        const date = new Date(dateString);
        
        // Verificar si la fecha es válida
        if (isNaN(date.getTime())) {
            return 'Fecha inválida';
        }
        
        // Formato: "15 Jun 2025, 14:30"
        const options = {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        };
        
        return date.toLocaleDateString('es-ES', options);
    } catch (error) {
        console.error('Error formateando fecha:', error);
        return 'Error en fecha';
    }
}

/**
 * Formatear fecha relativa (hace X tiempo)
 */
function formatRelativeDate(dateString) {
    if (!dateString) return 'Fecha no disponible';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffInMs = now - date;
        const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
        const diffInHours = Math.floor(diffInMinutes / 60);
        const diffInDays = Math.floor(diffInHours / 24);
        
        if (diffInMinutes < 1) return 'Ahora mismo';
        if (diffInMinutes < 60) return `Hace ${diffInMinutes} min`;
        if (diffInHours < 24) return `Hace ${diffInHours}h`;
        if (diffInDays < 7) return `Hace ${diffInDays} días`;
        
        // Para fechas más antiguas, usar formato completo
        return formatDate(dateString);
    } catch (error) {
        console.error('Error formateando fecha relativa:', error);
        return formatDate(dateString);
    }
}

// Exportar funciones globalmente
window.escapeHtml = escapeHtml;
window.formatDate = formatDate;
window.formatRelativeDate = formatRelativeDate;
window.setButtonLoading = setButtonLoading;
window.clearForm = clearForm;
window.switchTab = switchTab;
window.scrollToSection = scrollToSection;
window.toggleExamples = toggleExamples;
window.initializeTabs = initializeTabs;

// Inicializar tabs automáticamente cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initializeTabs, 100);
    });
} else {
    setTimeout(initializeTabs, 100);
}

console.log('✅ Utilidades de seguridad y formato cargadas');
console.log('✅ Funciones UI exportadas:', {
    escapeHtml: typeof window.escapeHtml,
    formatDate: typeof window.formatDate,
    formatRelativeDate: typeof window.formatRelativeDate,
    setButtonLoading: typeof window.setButtonLoading,
    clearForm: typeof window.clearForm,
    switchTab: typeof window.switchTab,
    scrollToSection: typeof window.scrollToSection,
    toggleExamples: typeof window.toggleExamples,
    initializeTabs: typeof window.initializeTabs
});
console.log('🎯 Sistema de pestañas inicializado automáticamente');
