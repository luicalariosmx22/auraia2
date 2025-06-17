// Archivo: clientes/aura/static/js/estadisticas_ads.js

document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('btn-generar-reporte');
  const status = document.getElementById('reporte-status');
  if (btn) {
    btn.onclick = async function() {
      btn.disabled = true;
      btn.textContent = 'Generando...';
      status.textContent = '';
      try {
        const resp = await fetch(window.location.pathname, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
          status.textContent = `✅ Reporte generado. Registros insertados: ${data.insertados}`;
          status.className = 'mt-4 text-center text-lg text-green-700';
        } else {
          status.textContent = 'Ocurrió un error al generar el reporte.';
          status.className = 'mt-4 text-center text-lg text-red-700';
        }
      } catch (e) {
        status.textContent = 'Error de red o del servidor.';
        status.className = 'mt-4 text-center text-lg text-red-700';
      }
      btn.disabled = false;
      btn.textContent = 'Generar/Actualizar Reporte Meta Ads';
    };
  }

  // Botón de eliminar reportes
  const btnEliminar = document.getElementById('btn-eliminar-reportes');
  if(btnEliminar) {
    btnEliminar.addEventListener('click', async () => {
      if(!confirm('¿Estás seguro de que deseas eliminar TODOS los reportes de Meta Ads? Esta acción no se puede deshacer.')) return;
      btnEliminar.disabled = true;
      statusDiv.textContent = 'Eliminando todos los reportes...';
      const nombreNora = document.body.dataset.nora;
      try {
        const resp = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas/eliminar_reportes`, {method: 'POST'});
        const data = await resp.json();
        if(data.ok) {
          statusDiv.textContent = `Reportes eliminados: ${data.eliminados}`;
        } else {
          statusDiv.textContent = 'Error al eliminar reportes: ' + (data.error || 'Error desconocido');
        }
      } catch(e) {
        statusDiv.textContent = 'Error al eliminar reportes: ' + e;
      }
      btnEliminar.disabled = false;
    });
  }

  const btnAbrirModalSync = document.getElementById("btn-abrir-modal-sync");
  if (btnAbrirModalSync) {
    btnAbrirModalSync.addEventListener("click", function() {
      cargarColumnasDisponibles();
    });
  }

  // --- ELIMINADO BLOQUE DE REPORTES DISPONIBLES ---
});

async function cargarEstadisticas() {
  const cont = document.getElementById('estadisticas-contenido');
  cont.innerHTML = '<div class="text-center text-blue-600">Cargando estadísticas...</div>';
  const nombreNora = document.body.dataset.nora;
  try {
    const resp = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas/data`);
    const data = await resp.json();
    if (!data.ok || !Array.isArray(data.reportes)) {
      cont.innerHTML = '<div class="text-red-600">No se pudieron cargar los reportes.</div>';
      return;
    }
    if (!data.reportes.length) {
      cont.innerHTML = '<div class="text-gray-500">No hay reportes semanales generados aún.</div>';
      return;
    }
    renderTablaYGraficas(data.reportes, cont, nombreNora);
  } catch (e) {
    cont.innerHTML = '<div class="text-red-600">Error de red al cargar estadísticas.</div>';
  }
}

function renderTablaYGraficas(reportes, cont, nombreNora) {
  let html = `<table class="min-w-full text-sm border border-gray-200 rounded-lg overflow-hidden mb-8">
    <thead class="bg-indigo-50">
      <tr>
        <th class="px-4 py-2">Empresa</th>
        <th class="px-4 py-2">Cuenta</th>
        <th class="px-4 py-2">Periodo</th>
        <th class="px-4 py-2">Gasto Total</th>
        <th class="px-4 py-2">FB</th>
        <th class="px-4 py-2">IG</th>
        <th class="px-4 py-2">Acciones</th>
      </tr>
    </thead>
    <tbody>`;
  for (const rep of reportes) {
    html += `<tr class="border-b hover:bg-indigo-50 transition">
      <td class="px-4 py-2">${rep.empresa_nombre || '-'}</td>
      <td class="px-4 py-2">${rep.id_cuenta_publicitaria || '-'}</td>
      <td class="px-4 py-2">${rep.fecha_inicio || ''} a ${rep.fecha_fin || ''}</td>
      <td class="px-4 py-2 font-mono text-green-700 font-semibold">$${(rep.importe_gastado_anuncios||0).toFixed(2)}</td>
      <td class="px-4 py-2 text-blue-700 font-semibold">$${(rep.facebook_importe_gastado||0).toFixed(2)}</td>
      <td class="px-4 py-2 text-pink-700 font-semibold">$${(rep.instagram_importe_gastado||0).toFixed(2)}</td>
      <td class="px-4 py-2">
        <a href="/panel_cliente/${nombreNora}/meta_ads/estadisticas/reporte/${rep.id}" class="text-blue-700 hover:underline font-semibold">Ver</a>
      </td>
    </tr>`;
  }
  html += '</tbody></table>';

  // Las gráficas no cambian (por ahora)
  html += `<div class='grid grid-cols-1 md:grid-cols-2 gap-8'>
    <div><canvas id='grafica_gasto'></canvas></div>
    <div><canvas id='grafica_impresiones'></canvas></div>
  </div>`;
  cont.innerHTML = html;

  const semanas = reportes.map(r => `${r.fecha_inicio} a ${r.fecha_fin}`).reverse();
  const gastos = reportes.map(r => r.importe_gastado_anuncios || 0).reverse();
  const impresiones = reportes.map(r => r.impresiones || 0).reverse();
  if (window.graficaGasto) window.graficaGasto.destroy();
  if (window.graficaImpresiones) window.graficaImpresiones.destroy();
  window.graficaGasto = new Chart(document.getElementById('grafica_gasto'), {
    type: 'line',
    data: {
      labels: semanas,
      datasets: [{
        label: 'Gasto semanal ($)',
        data: gastos,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99,102,241,0.1)',
        fill: true
      }]
    },
    options: {responsive: true, plugins: {legend: {display: true}}}
  });
  window.graficaImpresiones = new Chart(document.getElementById('grafica_impresiones'), {
    type: 'bar',
    data: {
      labels: semanas,
      datasets: [{
        label: 'Impresiones',
        data: impresiones,
        backgroundColor: '#818cf8'
      }]
    },
    options: {responsive: true, plugins: {legend: {display: true}}}
  });
}

async function cargarColumnasDisponibles() {
  const colDiv = document.getElementById("modal-columnas");
  colDiv.innerHTML = '<option>Cargando...</option>';
  try {
    const nombreNora = document.body.getAttribute('data-nora');
    const res = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas/columnas_disponibles`);
    const data = await res.json();
    if (data.ok && Array.isArray(data.columnas)) {
      colDiv.innerHTML = "";
      data.columnas.forEach(col => {
        const option = document.createElement("option");
        option.value = col;
        option.textContent = col;
        colDiv.appendChild(option);
      });
    } else {
      colDiv.innerHTML = '<option>Error al cargar columnas.</option>';
    }
  } catch (e) {
    colDiv.innerHTML = '<option>Error de red.</option>';
  }
}

// Limpieza del bloque de carga de columnas dinámicas (dentro de la función abrirModalSync o donde cargues columnas)
async function cargarColumnas() {
  const columnasSelect = document.getElementById("modal-columnas");
  const columnasError = document.getElementById("columnas-error");
  columnasSelect.innerHTML = '<option disabled>Cargando...</option>';
  columnasError.classList.add('hidden');
  try {
    const resp = await fetch('/api/meta_ads/columnas_anuncios_detalle');
    const data = await resp.json();
    columnasSelect.innerHTML = "";
    if (!data.ok || !Array.isArray(data.columnas)) {
      columnasError.textContent = 'Error al obtener columnas';
      columnasError.classList.remove('hidden');
      return;
    }
    for (const col of data.columnas) {
      const opt = document.createElement("option");
      opt.value = col;
      opt.textContent = col;
      columnasSelect.appendChild(opt);
    }
  } catch (e) {
    columnasError.textContent = 'Error de red al cargar columnas';
    columnasError.classList.remove('hidden');
  }
}

// Cargar estadísticas al iniciar
cargarEstadisticas();
