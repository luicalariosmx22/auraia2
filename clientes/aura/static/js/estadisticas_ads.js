// Archivo: clientes/aura/static/js/estadisticas_ads.js

document.addEventListener('DOMContentLoaded', function() {
  // Cargar estadísticas automáticamente
  cargarEstadisticas();
  
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
          // Recargar estadísticas después de generar reporte
          cargarEstadisticas();
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
  console.log('[DEBUG] Iniciando carga de estadísticas...');
  const cont = document.getElementById('estadisticas-contenido');
  cont.innerHTML = '<div class="text-center text-blue-600">Cargando estadísticas...</div>';
  const nombreNora = document.body.dataset.nora;
  console.log('[DEBUG] Nombre Nora:', nombreNora);
  try {
    const resp = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas/data`);
    const data = await resp.json();
    console.log('[DEBUG] Datos recibidos:', data);
    if (!data.ok || !Array.isArray(data.reportes)) {
      cont.innerHTML = '<div class="text-red-600">No se pudieron cargar los reportes.</div>';
      return;
    }
    if (!data.reportes.length) {
      cont.innerHTML = '<div class="text-gray-500">No hay reportes semanales generados aún.</div>';
      return;
    }
    console.log('[DEBUG] Reportes encontrados:', data.reportes.length);
    if (data.reportes.length > 0) {
      console.log('[DEBUG] Primer reporte:', data.reportes[0]);
    }
    renderTablaYGraficas(data.reportes, cont, nombreNora);
  } catch (e) {
    console.error('[ERROR] Error al cargar estadísticas:', e);
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
      <td class="px-4 py-2">${rep.empresa_nombre || 'Sin empresa'}</td>
      <td class="px-4 py-2">${rep.id_cuenta_publicitaria || '-'}</td>
      <td class="px-4 py-2">${rep.fecha_inicio || ''} a ${rep.fecha_fin || ''}</td>
      <td class="px-4 py-2 font-mono text-green-700 font-semibold">$${(rep.importe_gastado_anuncios||0).toFixed(2)}</td>
      <td class="px-4 py-2 text-blue-700 font-semibold">$${(rep.facebook_importe_gastado||0).toFixed(2)}</td>
      <td class="px-4 py-2 text-pink-700 font-semibold">$${(rep.instagram_importe_gastado||0).toFixed(2)}</td>
      <td class="px-4 py-2">
        <div class="flex gap-2">
          <a href="/panel_cliente/${nombreNora}/meta_ads/estadisticas/reporte/${rep.id}" 
             class="text-blue-700 hover:underline font-semibold text-xs px-2 py-1 bg-blue-50 rounded">
             👁️ Ver
          </a>
          <button onclick="compartirReporte('${rep.id}', '${rep.empresa_nombre || 'Sin empresa'}', '${rep.fecha_inicio}', '${rep.fecha_fin}')" 
                  class="text-green-700 hover:underline font-semibold text-xs px-2 py-1 bg-green-50 rounded border-0 cursor-pointer">
                  🔗 Compartir
          </button>
          <button onclick="descargarReporte('${rep.id}', '${rep.empresa_nombre || 'Sin empresa'}', '${rep.fecha_inicio}', '${rep.fecha_fin}')" 
                  class="text-orange-700 hover:underline font-semibold text-xs px-2 py-1 bg-orange-50 rounded border-0 cursor-pointer">
                  📊 Descargar
          </button>
        </div>
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

// Funciones para acciones específicas de reportes
async function compartirReporte(reporteId, empresaNombre, fechaInicio, fechaFin) {
  const statusDiv = document.getElementById('reporte-status');
  const nombreNora = document.body.dataset.nora;
  
  statusDiv.textContent = 'Generando link para compartir...';
  statusDiv.className = 'mt-4 text-center text-lg text-blue-600';
  
  try {
    const resp = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas/compartir_reporte`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        reporte_id: reporteId,
        empresa_nombre: empresaNombre,
        periodo: `${fechaInicio} a ${fechaFin}`
      })
    });
    
    const data = await resp.json();
    if (data.ok) {
      // Copiar al portapapeles
      await navigator.clipboard.writeText(data.url_publico);
      
      // Mostrar modal o mensaje con el link
      mostrarModalCompartir(data.url_publico, empresaNombre, fechaInicio, fechaFin);
      
      statusDiv.innerHTML = `✅ Link público generado y copiado al portapapeles`;
      statusDiv.className = 'mt-4 text-center text-lg text-green-600';
    } else {
      statusDiv.textContent = 'Error al generar link: ' + (data.error || 'Error desconocido');
      statusDiv.className = 'mt-4 text-center text-lg text-red-600';
    }
  } catch (e) {
    statusDiv.textContent = 'Error al generar link: ' + e.message;
    statusDiv.className = 'mt-4 text-center text-lg text-red-600';
  }
}

async function descargarReporte(reporteId, empresaNombre, fechaInicio, fechaFin) {
  const statusDiv = document.getElementById('reporte-status');
  const nombreNora = document.body.dataset.nora;
  
  statusDiv.textContent = 'Preparando descarga...';
  statusDiv.className = 'mt-4 text-center text-lg text-blue-600';
  
  try {
    const resp = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas/descargar_reporte`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        reporte_id: reporteId,
        formato: 'excel' // o 'pdf'
      })
    });
    
    if (resp.ok) {
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Meta_Ads_${empresaNombre}_${fechaInicio}_${fechaFin}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      statusDiv.textContent = '✅ Reporte descargado exitosamente';
      statusDiv.className = 'mt-4 text-center text-lg text-green-600';
    } else {
      const data = await resp.json();
      statusDiv.textContent = 'Error al descargar: ' + (data.error || 'Error desconocido');
      statusDiv.className = 'mt-4 text-center text-lg text-red-600';
    }
  } catch (e) {
    statusDiv.textContent = 'Error al descargar: ' + e.message;
    statusDiv.className = 'mt-4 text-center text-lg text-red-600';
  }
}

function mostrarModalCompartir(urlPublico, empresaNombre, fechaInicio, fechaFin) {
  // Crear modal dinámicamente
  const modal = document.createElement('div');
  modal.id = 'modal-compartir';
  modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
  modal.innerHTML = `
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-6 mx-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold text-gray-800">🔗 Compartir Reporte</h3>
        <button onclick="cerrarModalCompartir()" class="text-gray-500 hover:text-gray-700 text-xl">×</button>
      </div>
      
      <div class="mb-4">
        <p class="text-sm text-gray-600 mb-2">
          <strong>Empresa:</strong> ${empresaNombre}<br>
          <strong>Período:</strong> ${fechaInicio} a ${fechaFin}
        </p>
      </div>
      
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Link público:</label>
        <div class="flex">
          <input type="text" id="link-compartir" value="${urlPublico}" 
                 class="flex-1 px-3 py-2 border border-gray-300 rounded-l-md text-sm" readonly>
          <button onclick="copiarLink()" 
                  class="px-4 py-2 bg-blue-600 text-white rounded-r-md text-sm hover:bg-blue-700">
                  📋 Copiar
          </button>
        </div>
      </div>
      
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Compartir por:</label>
        <div class="flex gap-2">
          <button onclick="compartirWhatsApp('${urlPublico}')" 
                  class="px-3 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                  📱 WhatsApp
          </button>
          <button onclick="compartirEmail('${urlPublico}', '${empresaNombre}')" 
                  class="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                  📧 Email
          </button>
          <button onclick="compartirTelegram('${urlPublico}')" 
                  class="px-3 py-2 bg-sky-600 text-white rounded text-sm hover:bg-sky-700">
                  ✈️ Telegram
          </button>
        </div>
      </div>
      
      <div class="flex justify-end">
        <button onclick="cerrarModalCompartir()" 
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">
                Cerrar
        </button>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
}

function cerrarModalCompartir() {
  const modal = document.getElementById('modal-compartir');
  if (modal) {
    document.body.removeChild(modal);
  }
}

async function copiarLink() {
  const linkInput = document.getElementById('link-compartir');
  await navigator.clipboard.writeText(linkInput.value);
  
  // Feedback visual
  const button = event.target;
  const originalText = button.textContent;
  button.textContent = '✅ Copiado';
  button.className = button.className.replace('bg-blue-600', 'bg-green-600');
  
  setTimeout(() => {
    button.textContent = originalText;
    button.className = button.className.replace('bg-green-600', 'bg-blue-600');
  }, 2000);
}

function compartirWhatsApp(url) {
  const mensaje = `📊 Aquí tienes tu reporte de Meta Ads: ${url}`;
  window.open(`https://wa.me/?text=${encodeURIComponent(mensaje)}`, '_blank');
}

function compartirEmail(url, empresaNombre) {
  const asunto = `Reporte Meta Ads - ${empresaNombre}`;
  const mensaje = `Hola,\n\nAquí tienes tu reporte detallado de Meta Ads:\n\n${url}\n\nSaludos!`;
  window.open(`mailto:?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(mensaje)}`, '_blank');
}

function compartirTelegram(url) {
  const mensaje = `📊 Tu reporte de Meta Ads: ${url}`;
  window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(mensaje)}`, '_blank');
}
