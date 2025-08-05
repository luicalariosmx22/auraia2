/**
 * Panel de Alertas - JavaScript
 * Funciones para gestionar las alertas del sistema
 */

// Función para toggle del acordeón
function toggleAccordion(tipo) {
    const content = document.getElementById(`content-${tipo}`);
    const chevron = document.getElementById(`chevron-${tipo}`);
    
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        chevron.style.transform = 'rotate(90deg)';
    } else {
        content.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
    }
}

async function notificarAlerta(alertaId) {
    if (confirm('¿Enviar notificación por email/WhatsApp de esta alerta?')) {
        try {
            const response = await fetch(`notificar/${alertaId}`, { method: 'POST' });
            const result = await response.json();
            
            if (response.ok) {
                alert(`✅ ${result.mensaje}`);
                location.reload();
            } else {
                alert(`❌ ${result.error || 'Error al enviar notificación'}`);
            }
        } catch (error) {
            console.error('Error al enviar notificación:', error);
            alert('Error de conexión al enviar notificación');
        }
    }
}

async function marcarVista(alertaId) {
    try {
        const response = await fetch(`marcar_vista/${alertaId}`, { method: 'POST' });
        if (response.ok) {
            location.reload();
        } else {
            alert('Error al marcar como vista');
        }
    } catch (error) {
        console.error('Error al marcar vista:', error);
        alert('Error de conexión');
    }
}

async function resolverAlerta(alertaId) {
    if (confirm('¿Estás seguro de que quieres marcar esta alerta como resuelta?')) {
        try {
            const response = await fetch(`resolver/${alertaId}`, { method: 'POST' });
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al resolver alerta');
            }
        } catch (error) {
            console.error('Error al resolver alerta:', error);
            alert('Error de conexión');
        }
    }
}

async function ignorarAlerta(alertaId) {
    if (confirm('¿Estás seguro de que quieres ignorar esta alerta? No volverá a aparecer aunque se detecte de nuevo.')) {
        try {
            const response = await fetch(`ignorar/${alertaId}`, { method: 'POST' });
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al ignorar alerta');
            }
        } catch (error) {
            console.error('Error al ignorar alerta:', error);
            alert('Error de conexión');
        }
    }
}

async function eliminarAlerta(alertaId) {
    if (confirm('¿Estás seguro de que quieres eliminar esta alerta?')) {
        try {
            const response = await fetch(`eliminar/${alertaId}`, { method: 'POST' });
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al eliminar alerta');
            }
        } catch (error) {
            console.error('Error al eliminar alerta:', error);
            alert('Error de conexión');
        }
    }
}
