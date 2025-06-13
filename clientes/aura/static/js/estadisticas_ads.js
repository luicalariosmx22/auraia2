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
      btn.textContent = 'Generar/Actualizar Reporte Semanal';
    };
  }

  // --- Sincronización de anuncios Meta Ads ---
  const btnSync = document.getElementById('btn-sincronizar-anuncios');
  const statusDiv = document.getElementById('reporte-status');
  if (btnSync) {
    btnSync.addEventListener('click', async () => {
      btnSync.disabled = true;
      statusDiv.textContent = 'Sincronizando anuncios de Meta Ads...';
      const nombreNora = document.body.dataset.nora;
      let url = `/panel_cliente/${nombreNora}/meta_ads/estadisticas/sync`;
      try {
        const resp = await fetch(url, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
          let msg = `Sincronización completada. Anuncios procesados: ${data.procesados}`;
          if (data.procesados === 0) {
            msg += `<br><span class='text-red-700 font-bold'>No se insertaron anuncios. Verifica el token de Meta, permisos de la cuenta o si ya existen los anuncios para este periodo.</span>`;
          }
          if (Array.isArray(data.sin_anuncios) && data.sin_anuncios.length > 0) {
            msg += `<br><span class='text-red-700 font-bold'>Cuentas sin anuncios:</span><ul class='list-disc list-inside'>`;
            for (const c of data.sin_anuncios) {
              msg += `<li><b>${c.nombre_cliente || 'Sin nombre'}</b> (ID: ${c.id_cuenta_publicitaria})</li>`;
            }
            msg += '</ul>';
          }
          statusDiv.innerHTML = msg;
        } else {
          statusDiv.textContent = 'Error en la sincronización: ' + (data.error || 'Error desconocido');
        }
      } catch (e) {
        statusDiv.textContent = 'Error en la sincronización: ' + e;
      }
      btnSync.disabled = false;
    });
  }

  // Botón de eliminar reportes
  const btnEliminar = document.getElementById('btn-eliminar-reportes');
  if(btnEliminar) {
    btnEliminar.addEventListener('click', async () => {
      if(!confirm('¿Estás seguro de que deseas eliminar TODOS los reportes semanales? Esta acción no se puede deshacer.')) return;
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
        <a href="/panel_cliente/${nombreNora}/meta_ads/estadisticas/reporte/${rep.id}" class="text-blue-700 hover:underline font-semibold">Ver detalle</a>
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

// Cargar estadísticas al iniciar
cargarEstadisticas();
