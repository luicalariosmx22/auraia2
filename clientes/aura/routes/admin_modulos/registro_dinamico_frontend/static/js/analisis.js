/**
 * JavaScript para el panel de análisis del registro dinámico
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const btnActualizar = document.getElementById('btn-actualizar');
    const btnExportar = document.getElementById('btn-exportar');
    const alertasCont = document.getElementById('alertas-container');
    const cargandoIndicador = document.getElementById('cargando-indicador');
    
    // Inicializar tooltips
    inicializarTooltips();
    
    // Renderizar gráficos si existen los contenedores
    if (document.getElementById('grafico-salud')) {
        renderizarGraficoSalud();
    }
    
    if (document.getElementById('grafico-modulos')) {
        renderizarGraficoModulos();
    }
    
    if (document.getElementById('grafico-dependencias') && window.dataDependencias) {
        renderizarGrafoDependencias();
    }
    
    // Eventos
    if (btnActualizar) {
        btnActualizar.addEventListener('click', actualizarAnalisis);
    }
    
    if (btnExportar) {
        btnExportar.addEventListener('click', function() {
            window.location.href = '/admin/registro_dinamico/api/exportar';
        });
    }
    
    // Mostrar detalles de alertas al hacer clic
    document.querySelectorAll('.alerta-expandible').forEach(item => {
        item.addEventListener('click', function() {
            const detalleId = this.getAttribute('data-detalle');
            const detalle = document.getElementById(detalleId);
            
            if (detalle.classList.contains('hidden')) {
                detalle.classList.remove('hidden');
                this.querySelector('.icono-expandir').innerHTML = '&minus;';
            } else {
                detalle.classList.add('hidden');
                this.querySelector('.icono-expandir').innerHTML = '&plus;';
            }
        });
    });
});

/**
 * Inicializa tooltips para elementos con atributo data-tooltip
 */
function inicializarTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(elemento => {
        elemento.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-50 bg-gray-800 text-white text-xs rounded py-1 px-2 -mt-12';
            tooltip.innerHTML = this.getAttribute('data-tooltip');
            tooltip.style.maxWidth = '200px';
            
            this.appendChild(tooltip);
        });
        
        elemento.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.absolute.z-50');
            if (tooltip) {
                this.removeChild(tooltip);
            }
        });
    });
}

/**
 * Actualiza el análisis del registro dinámico mediante la API
 */
async function actualizarAnalisis() {
    try {
        const btnActualizar = document.getElementById('btn-actualizar');
        const cargandoIndicador = document.getElementById('cargando-indicador');
        
        // Mostrar indicador de carga
        btnActualizar.disabled = true;
        cargandoIndicador.classList.remove('hidden');
        
        // Llamar a la API para actualizar el análisis
        const response = await fetch('/admin/registro_dinamico/api/actualizar_analisis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.error) {
            mostrarAlerta('Error al actualizar análisis: ' + data.error, 'error');
        } else {
            mostrarAlerta(`Análisis actualizado. ${data.modulos_analizados} módulos analizados.`, 'success');
            // Recargar la página para mostrar los datos actualizados
            setTimeout(() => window.location.reload(), 1500);
        }
    } catch (error) {
        mostrarAlerta('Error de conexión: ' + error.message, 'error');
    } finally {
        // Ocultar indicador de carga y habilitar botón
        document.getElementById('btn-actualizar').disabled = false;
        document.getElementById('cargando-indicador').classList.add('hidden');
    }
}

/**
 * Muestra una alerta en la interfaz
 * 
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de alerta (success, error, warning)
 */
function mostrarAlerta(mensaje, tipo = 'info') {
    const alertasCont = document.getElementById('alertas-container');
    if (!alertasCont) return;
    
    const colores = {
        success: 'bg-green-100 border-green-500 text-green-700',
        error: 'bg-red-100 border-red-500 text-red-700',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
        info: 'bg-blue-100 border-blue-500 text-blue-700'
    };
    
    const alerta = document.createElement('div');
    alerta.className = `p-3 mb-3 border-l-4 ${colores[tipo]} fade-in`;
    alerta.innerHTML = mensaje;
    
    alertasCont.appendChild(alerta);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        alerta.classList.add('fade-out');
        setTimeout(() => alertasCont.removeChild(alerta), 500);
    }, 5000);
}

/**
 * Renderiza un gráfico circular para la salud del código
 */
function renderizarGraficoSalud() {
    const ctx = document.getElementById('grafico-salud').getContext('2d');
    
    // Obtener datos del elemento data
    const datos = JSON.parse(document.getElementById('datos-salud').textContent);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Seguridad', 'Calidad'],
            datasets: [{
                data: [
                    datos.puntuacion_seguridad_promedio,
                    datos.puntuacion_calidad_promedio
                ],
                backgroundColor: [
                    '#3B82F6', // Azul para seguridad
                    '#10B981'  // Verde para calidad
                ],
                borderColor: '#FFFFFF',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.raw.toFixed(1) + '/100';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Renderiza un gráfico de barras para los módulos
 */
function renderizarGraficoModulos() {
    const ctx = document.getElementById('grafico-modulos').getContext('2d');
    
    // Obtener datos del elemento data
    const datos = JSON.parse(document.getElementById('datos-modulos').textContent);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: datos.nombres,
            datasets: [{
                label: 'Complejidad',
                data: datos.complejidad,
                backgroundColor: datos.colores,
                borderColor: '#FFFFFF',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Complejidad'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Módulos'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            return [
                                `Seguridad: ${datos.seguridad[index]}/100`,
                                `Calidad: ${datos.calidad[index]}/100`
                            ];
                        }
                    }
                }
            }
        }
    });
}

/**
 * Renderiza un grafo de dependencias entre módulos usando vis.js
 */
function renderizarGrafoDependencias() {
    // Obtener datos del elemento data
    const dataDependencias = window.dataDependencias;
    
    if (!dataDependencias || !dataDependencias.grafo) return;
    
    const nodos = [];
    const aristas = [];
    const colores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
    
    // Crear nodos
    let i = 0;
    const modulos = Object.keys(dataDependencias.grafo);
    
    modulos.forEach(modulo => {
        nodos.push({
            id: modulo,
            label: modulo,
            color: colores[i % colores.length],
            shape: 'dot',
            size: 10 + (dataDependencias.grafo[modulo].length * 3)
        });
        i++;
    });
    
    // Crear aristas
    modulos.forEach(modulo => {
        dataDependencias.grafo[modulo].forEach(dependencia => {
            aristas.push({
                from: modulo,
                to: dependencia,
                arrows: 'to',
                color: { color: '#64748B' }
            });
        });
    });
    
    // Crear el grafo
    const container = document.getElementById('grafico-dependencias');
    
    const datos = {
        nodes: new vis.DataSet(nodos),
        edges: new vis.DataSet(aristas)
    };
    
    const opciones = {
        physics: {
            stabilization: true,
            barnesHut: {
                springConstant: 0.04,
                springLength: 100
            }
        },
        layout: {
            hierarchical: {
                enabled: false
            }
        }
    };
    
    new vis.Network(container, datos, opciones);
}