// Manejo de modales
window.modal = {
    element: null,
    config: {
        closeOnEscape: true,
        closeOnClickOutside: true,
        animationDuration: 300
    },

    init() {
        this.element = document.getElementById('modal-diagnostico');
        this.setupEventListeners();
    },

    setupEventListeners() {
        // Cerrar con Escape
        if (this.config.closeOnEscape) {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !this.element.classList.contains('hidden')) {
                    this.cerrar();
                }
            });
        }

        // Cerrar al hacer clic fuera
        if (this.config.closeOnClickOutside) {
            this.element.addEventListener('click', (e) => {
                if (e.target === this.element) {
                    this.cerrar();
                }
            });
        }

        // Botones de cerrar
        this.element.querySelectorAll('[data-modal-close]').forEach(btn => {
            btn.addEventListener('click', () => this.cerrar());
        });
    },

    abrir() {
        this.element.classList.remove('hidden');
        this.element.classList.add('flex');
        document.body.style.overflow = 'hidden';
    },

    cerrar() {
        this.element.classList.remove('flex');
        this.element.classList.add('hidden');
        document.body.style.overflow = '';
        
        // Limpiar estado
        document.getElementById('detalles-error').classList.add('hidden');
        document.getElementById('detalles-exito').classList.add('hidden');
        document.getElementById('btn-reintentar').classList.add('hidden');
    },

    mostrarCarga() {
        // Implementar animación de carga si es necesario
    },

    ocultarCarga() {
        // Ocultar animación de carga si es necesario
    }
};

// Inicializar el modal cuando el documento esté listo
document.addEventListener('DOMContentLoaded', () => modal.init());
