// JS para la carga manual de Reporte Meta Ads
// Solo feedback visual y UX para carga y confirmación

document.addEventListener('DOMContentLoaded', function() {
    // Feedback visual y evitar doble submit en carga manual
    const formCarga = document.getElementById('form-reporte-manual');
    if (formCarga) {
        formCarga.addEventListener('submit', function(e) {
            const btn = formCarga.querySelector('button[type="submit"],button:not([type])');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="animate-spin mr-2">⏳</span>Cargando...';
            }
            let feedback = document.getElementById('feedback');
            if (feedback) feedback.textContent = 'Cargando archivo, por favor espera...';
        });
    }
    // UX para submit de confirmación
    const formConfirmar = document.getElementById('form-confirmar-reporte');
    if (formConfirmar) {
        formConfirmar.addEventListener('submit', function(e) {
            const btn = formConfirmar.querySelector('button[type="submit"],button:not([type])');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="animate-spin mr-2">⏳</span>Guardando...';
            }
            let feedback = document.getElementById('feedback');
            if (feedback) feedback.textContent = 'Guardando en base de datos, por favor espera...';
        });
    }
    // Scroll automático al feedback tras submit
    const feedback = document.getElementById('feedback');
    if (feedback) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
