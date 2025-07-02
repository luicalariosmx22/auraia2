/**
 * Componente de botón para actualizar datos de Google Ads de los últimos 7 días
 * 
 * Este componente añade un botón a la interfaz de usuario que permite
 * actualizar los datos de Google Ads de los últimos 7 días con un solo clic.
 */

// Clase para el botón de actualización
class GoogleAdsUpdateButton {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.isUpdating = false;
        
        if (!this.container) {
            console.error(`Container with id '${containerId}' not found`);
            return;
        }
        
        this.init();
    }
    
    init() {
        // Crear el botón y añadirlo al contenedor
        this.createButton();
        
        // Añadir el contenedor para mostrar el estado
        this.createStatusContainer();
    }
    
    createButton() {
        // Crear el botón con estilo Bootstrap
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-primary btn-update-google-ads';
        button.setAttribute('data-bs-toggle', 'tooltip');
        button.setAttribute('data-bs-placement', 'top');
        button.setAttribute('title', 'Actualiza los datos de Google Ads de los últimos 7 días');
        
        // Añadir icono y texto
        button.innerHTML = `
            <i class="fas fa-sync-alt me-2"></i>
            Actualizar datos últimos 7 días
        `;
        
        // Añadir evento de clic
        button.addEventListener('click', () => this.handleUpdateClick());
        
        // Añadir al contenedor
        this.container.appendChild(button);
        this.button = button;
        
        // Inicializar tooltip
        try {
            new bootstrap.Tooltip(button);
        } catch (e) {
            console.warn('Bootstrap tooltip not initialized', e);
        }
    }
    
    createStatusContainer() {
        // Crear contenedor para mostrar el estado de la actualización
        const statusContainer = document.createElement('div');
        statusContainer.className = 'google-ads-update-status mt-3';
        statusContainer.style.display = 'none';
        
        // Añadir al contenedor principal
        this.container.appendChild(statusContainer);
        this.statusContainer = statusContainer;
    }
    
    handleUpdateClick() {
        if (this.isUpdating) {
            return; // Evitar múltiples clics durante la actualización
        }
        
        // Confirmar la acción
        if (!confirm('¿Estás seguro de que deseas actualizar los datos de Google Ads de los últimos 7 días? Esta operación puede tardar varios minutos.')) {
            return;
        }
        
        // Iniciar actualización
        this.setUpdatingState(true);
        this.updateStatus('Iniciando actualización de datos...', 'info');
        
        // Llamar al endpoint
        fetch('/api/google-ads/actualizar-ultimos-7-dias', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                incluir_mcc: false,
                incluir_anuncios: true
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error en la respuesta: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Actualización exitosa
                const resultado = data.resultado || {};
                const cuentas = resultado.cuentas_procesadas || 0;
                const keywords = resultado.keywords_totales || 0;
                const anuncios = resultado.anuncios_totales || 0;
                
                this.updateStatus(
                    `✅ Actualización completada correctamente.<br>
                     📊 Cuentas actualizadas: ${cuentas}<br>
                     🔑 Keywords actualizadas: ${keywords}<br>
                     📝 Anuncios actualizados: ${anuncios}`,
                    'success'
                );
                
                // Notificar al usuario que debe actualizar la página para ver los cambios
                setTimeout(() => {
                    alert('Actualización completada. Por favor, actualiza la página para ver los cambios más recientes.');
                }, 500);
            } else {
                // Error en la actualización
                this.updateStatus(
                    `❌ Error en la actualización: ${data.error || 'Error desconocido'}`,
                    'danger'
                );
            }
        })
        .catch(error => {
            console.error('Error actualizando datos:', error);
            this.updateStatus(
                `❌ Error de conexión: ${error.message}`,
                'danger'
            );
        })
        .finally(() => {
            // Restaurar estado del botón
            this.setUpdatingState(false);
        });
    }
    
    setUpdatingState(isUpdating) {
        this.isUpdating = isUpdating;
        
        // Actualizar estado del botón
        if (isUpdating) {
            this.button.disabled = true;
            this.button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Actualizando...
            `;
        } else {
            this.button.disabled = false;
            this.button.innerHTML = `
                <i class="fas fa-sync-alt me-2"></i>
                Actualizar datos últimos 7 días
            `;
        }
    }
    
    updateStatus(message, type) {
        // Mostrar mensaje de estado
        this.statusContainer.style.display = 'block';
        this.statusContainer.innerHTML = `
            <div class="alert alert-${type}" role="alert">
                ${message}
            </div>
        `;
        
        // Si es un mensaje de éxito o error, mantenerlo visible
        if (type === 'success' || type === 'danger') {
            // No hacer nada, mantener el mensaje visible
        } else {
            // Para mensajes informativos, ocultar después de un tiempo
            setTimeout(() => {
                if (this.isUpdating) {
                    this.updateStatus('Actualización en progreso. Esto puede tardar varios minutos...', 'info');
                }
            }, 3000);
        }
    }
}

// Exportar la clase para su uso en otros archivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GoogleAdsUpdateButton;
}
