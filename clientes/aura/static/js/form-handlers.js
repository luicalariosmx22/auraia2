/**
 * 📝 FORM HANDLERS - Manejadores de Formularios AJAX
 * Funciones para enviar formularios mediante AJAX y manejar respuestas
 */

// =============================================================================
// 🚀 INICIALIZACIÓN DE MANEJADORES DE FORMULARIOS
// =============================================================================

/**
 * Inicializar todos los manejadores de formularios
 */
function initializeFormHandlers() {
    initializeCharacterCounters();
    initializeAjaxForms();
    initializeKnowledgeForm();
    console.log('✅ Manejadores de formularios inicializados');
}

/**
 * Inicializar formularios AJAX
 */
function initializeAjaxForms() {
    const forms = [
        { id: 'form-personalidad', endpoint: 'personalidad', successMsg: 'Personalidad actualizada correctamente' },
        { id: 'form-instrucciones', endpoint: 'instrucciones', successMsg: 'Instrucciones actualizadas correctamente' },
        { id: 'form-estado-ia', endpoint: 'estadoIA', successMsg: 'Estado de IA actualizado correctamente' },
        { id: 'form-limites', endpoint: 'limites', successMsg: 'Límites actualizados correctamente' },
        { id: 'form-bienvenida', endpoint: 'bienvenida', successMsg: 'Mensaje de bienvenida actualizado correctamente' }
    ];
    
    forms.forEach(({ id, endpoint, successMsg }) => {
        const form = document.getElementById(id);
        if (form) {
            form.addEventListener('submit', (e) => handleAjaxFormSubmit(e, endpoint, successMsg));
        }
    });
}

/**
 * Inicializar formulario de conocimiento
 */
function initializeKnowledgeForm() {
    const form = document.getElementById('form-agregar-conocimiento');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            agregarBloque();
        });
    }
    
    // Contador de caracteres para contenido
    const contenidoTextarea = document.getElementById('nuevo-contenido');
    const contador = document.getElementById('contador-caracteres');
    
    if (contenidoTextarea && contador) {
        contenidoTextarea.addEventListener('input', () => {
            updateCharacterCounter(contenidoTextarea, contador, PANEL_CONFIG.limits.maxContentLength);
        });
    }
}

// =============================================================================
// 🔄 MANEJADORES DE FORMULARIOS AJAX
// =============================================================================

/**
 * Manejar envío de formulario AJAX genérico
 */
async function handleAjaxFormSubmit(event, endpoint, successMessage) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);
    
    if (!submitBtn) return;
    
    // Guardar texto original del botón
    const originalText = submitBtn.innerHTML;
    
    // Estado de carga
    setButtonLoading(submitBtn, true);
    
    try {
        const response = await fetch(PANEL_CONFIG.endpoints[endpoint], {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessAnimation(submitBtn, originalText);
            showToast(successMessage, 'success');
            
            // Marcar que se han guardado los cambios
            PANEL_STATE.unsavedChanges = false;
            
        } else {
            throw new Error(result.message || 'Error al procesar la solicitud');
        }
        
    } catch (error) {
        console.error('Error en formulario:', error);
        showErrorAnimation(submitBtn, originalText);
        showToast(error.message || 'Error al procesar la solicitud', 'error');
    }
}

/**
 * Manejar formulario de personalidad específicamente
 */
async function handlePersonalidadForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const textarea = form.querySelector('textarea[name="personalidad"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!textarea || !submitBtn) return;
    
    const personalidad = textarea.value.trim();
    
    if (!personalidad) {
        showToast('La personalidad no puede estar vacía', 'error');
        textarea.focus();
        return;
    }
    
    await handleAjaxFormSubmit(event, 'personalidad', 'Personalidad actualizada correctamente');
}

/**
 * Manejar formulario de instrucciones específicamente
 */
async function handleInstruccionesForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const textarea = form.querySelector('textarea[name="instrucciones"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!textarea || !submitBtn) return;
    
    const instrucciones = textarea.value.trim();
    
    if (!instrucciones) {
        showToast('Las instrucciones no pueden estar vacías', 'error');
        textarea.focus();
        return;
    }
    
    await handleAjaxFormSubmit(event, 'instrucciones', 'Instrucciones actualizadas correctamente');
}

/**
 * Manejar formulario de estado de IA
 */
async function handleEstadoIAForm(event) {
    event.preventDefault();
    await handleAjaxFormSubmit(event, 'estadoIA', 'Estado de IA actualizado correctamente');
}

/**
 * Manejar formulario de límites
 */
async function handleLimitesForm(event) {
    event.preventDefault();
    await handleAjaxFormSubmit(event, 'limites', 'Límites de respuesta actualizados correctamente');
}

/**
 * Manejar formulario de bienvenida
 */
async function handleBienvenidaForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const textarea = form.querySelector('textarea[name="bienvenida"]');
    
    if (textarea) {
        const bienvenida = textarea.value.trim();
        
        if (!bienvenida) {
            showToast('El mensaje de bienvenida no puede estar vacío', 'error');
            textarea.focus();
            return;
        }
    }
    
    await handleAjaxFormSubmit(event, 'bienvenida', 'Mensaje de bienvenida actualizado correctamente');
}

// =============================================================================
// 🎭 ANIMACIONES DE ESTADO DE BOTONES
// =============================================================================

/**
 * Mostrar animación de éxito en botón
 */
function showSuccessAnimation(button, originalText) {
    button.disabled = false;
    button.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span class="text-green-600">Guardado</span>
        </div>
    `;
    
    // Restaurar botón después de 2 segundos
    setTimeout(() => {
        button.innerHTML = originalText;
    }, 2000);
}

/**
 * Mostrar animación de error en botón
 */
function showErrorAnimation(button, originalText) {
    button.disabled = false;
    button.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <span class="text-red-600">Error</span>
        </div>
    `;
    
    // Restaurar botón después de 3 segundos
    setTimeout(() => {
        button.innerHTML = originalText;
    }, 3000);
}

/**
 * Mostrar estado de carga en botón (override para compatibilidad)
 */
function setButtonLoading(button, isLoading = true) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = `
            <div class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Guardando...
            </div>
        `;
    } else {
        button.disabled = false;
        // El texto original debería restaurarse en las funciones de éxito/error
    }
}

// =============================================================================
// 🔧 UTILIDADES DE FORMULARIOS
// =============================================================================

/**
 * Validar formulario antes de envío
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

/**
 * Limpiar errores de validación
 */
function clearValidationErrors(form) {
    const fields = form.querySelectorAll('.border-red-500');
    fields.forEach(field => {
        field.classList.remove('border-red-500');
    });
}

/**
 * Marcar formulario como modificado
 */
function markFormAsModified() {
    PANEL_STATE.unsavedChanges = true;
    
    // Opcional: mostrar indicador visual de cambios no guardados
    const indicator = document.getElementById('unsaved-changes-indicator');
    if (indicator) {
        indicator.classList.remove('hidden');
    }
}

/**
 * Marcar formulario como guardado
 */
function markFormAsSaved() {
    PANEL_STATE.unsavedChanges = false;
    
    // Ocultar indicador de cambios no guardados
    const indicator = document.getElementById('unsaved-changes-indicator');
    if (indicator) {
        indicator.classList.add('hidden');
    }
}

// =============================================================================
// 🔍 FUNCIONES DE NOTIFICACIÓN (LEGACY SUPPORT)
// =============================================================================

/**
 * Mostrar notificación (alias para showToast para compatibilidad)
 */
function mostrarNotificacion(message, type = 'info') {
    showToast(message, type);
}

// =============================================================================
// 🎮 EVENT LISTENERS ADICIONALES
// =============================================================================

// Detectar cambios en formularios para marcar como modificado
document.addEventListener('input', function(e) {
    if (e.target.closest('form')) {
        markFormAsModified();
    }
});

// Prevenir pérdida de datos al salir de la página
window.addEventListener('beforeunload', function(e) {
    if (PANEL_STATE.unsavedChanges) {
        e.preventDefault();
        e.returnValue = '¿Estás seguro de que quieres salir? Hay cambios sin guardar.';
        return e.returnValue;
    }
});
