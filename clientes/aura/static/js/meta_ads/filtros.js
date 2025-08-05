// Manejo de filtros para la tabla de cuentas publicitarias
const filtros = {
    init() {
        // Inicializar eventos de filtros
        ['input', 'change'].forEach(evento => {
            document.getElementById('filtro-empresa').addEventListener(evento, this.aplicarFiltros);
            document.getElementById('filtro-estado').addEventListener(evento, this.aplicarFiltros);
            document.getElementById('filtro-vinculo').addEventListener(evento, this.aplicarFiltros);
            document.getElementById('filtro-anuncios').addEventListener(evento, this.aplicarFiltros);
        });
    },

    aplicarFiltros() {
        const empresa = document.getElementById('filtro-empresa').value.toLowerCase();
        const estado = document.getElementById('filtro-estado').value;
        const vinculo = document.getElementById('filtro-vinculo').value;
        const anuncios = document.getElementById('filtro-anuncios').value;

        document.querySelectorAll('tbody tr').forEach(tr => {
            if (tr.querySelector('td')?.classList.contains('text-gray-400')) return; // fila vacía
            let mostrar = true;

            // Filtro empresa
            if (empresa) {
                const empresaCell = tr.querySelector('td:first-child').innerText.toLowerCase();
                const cuentaCell = tr.querySelector('td:nth-child(2)').innerText.toLowerCase();
                if (!empresaCell.includes(empresa) && !cuentaCell.includes(empresa)) mostrar = false;
            }

            // Filtro estado
            if (estado) {
                const esActiva = tr.querySelector('td:nth-child(3) span')?.textContent.includes('Activa');
                if (estado === '1' && !esActiva) mostrar = false;
                if (estado === '0' && esActiva) mostrar = false;
            }

            // Filtro empresa vinculada
            if (vinculo) {
                const vincularBtn = tr.querySelector('td:last-child a').textContent.trim();
                const tieneEmpresa = vincularBtn === 'Cambiar';
                if (vinculo === 'con_empresa' && !tieneEmpresa) mostrar = false;
                if (vinculo === 'sin_empresa' && tieneEmpresa) mostrar = false;
            }

            // Filtro anuncios activos
            if (anuncios) {
                const span = tr.querySelector('td:nth-child(4) span');
                const val = span ? span.textContent.trim() : '';
                if (anuncios === 'con_activos' && (!val || val === '—' || val === '0')) mostrar = false;
                if (anuncios === 'sin_activos' && val && val !== '—' && val !== '0') mostrar = false;
            }

            tr.style.display = mostrar ? '' : 'none';
        });
    }
};

// Inicializar filtros cuando el documento esté listo
document.addEventListener('DOMContentLoaded', () => filtros.init());
