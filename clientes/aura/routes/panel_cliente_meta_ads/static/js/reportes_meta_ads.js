// Archivo: panel_cliente_meta_ads/static/js/reportes_meta_ads.js

document.addEventListener('DOMContentLoaded', function() {
  console.log('[DEBUG] DOM Cargado, inicializando reportes_meta_ads.js');
  console.log('[DEBUG] nombre_nora:', document.body.dataset.nora);
  
  // Cargar reportes automáticamente
  cargarReportes();
});

function renderizarReportes(reportes) {
  const tbody = document.querySelector('.overflow-x-auto table tbody');
  if (!tbody) return;

  if (!reportes.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-gray-500">No hay reportes disponibles</td></tr>';
    return;
  }

  tbody.innerHTML = reportes.map(reporte => {
    // Calcular totales
    const gastoTotal = (reporte.importe_gastado_campañas || 0).toFixed(2);
    const fbImporte = (reporte.facebook_importe_gastado || 0).toFixed(2);
    const igImporte = (reporte.instagram_importe_gastado || 0).toFixed(2);
    
    return `
    <tr class="border-t hover:bg-gray-50">
      <td class="px-4 py-2">${reporte.empresa_nombre || 'Sin nombre'}</td>
      <td class="px-4 py-2">
        <div class="text-sm">
          <div>ID: ${reporte.id_cuenta_publicitaria || 'N/A'}</div>
          <div>Campañas: ${reporte.total_campañas || 0}</div>
          <div>Anuncios: ${reporte.total_anuncios || 0}</div>
        </div>
      </td>
      <td class="px-4 py-2">${formatearFecha(reporte.fecha_inicio)} - ${formatearFecha(reporte.fecha_fin)}</td>
      <td class="px-4 py-2">
        <div class="text-sm font-semibold">
          <div>$${formatearNumero(gastoTotal)}</div>
          <div class="text-xs text-gray-500">
            Clicks: ${formatearNumero(reporte.clicks || 0)}<br>
            Mensajes: ${formatearNumero(reporte.mensajes || 0)}
          </div>
        </div>
      </td>
      <td class="px-4 py-2">
        <div class="text-sm">
          <div class="font-semibold text-blue-700">Facebook</div>
          <div>Imp: ${formatearNumero(reporte.facebook_impresiones || 0)}</div>
          <div>Alc: ${formatearNumero(reporte.facebook_alcance || 0)}</div>
          <div>Clicks: ${formatearNumero(reporte.facebook_clicks || 0)}</div>
          <div>Msgs: ${formatearNumero(reporte.facebook_mensajes || 0)}</div>
          <div class="font-semibold">$${formatearNumero(fbImporte)}</div>
        </div>
      </td>
      <td class="px-4 py-2">
        <div class="text-sm">
          <div class="font-semibold text-pink-700">Instagram</div>
          <div>Imp: ${formatearNumero(reporte.instagram_impresiones || 0)}</div>
          <div>Alc: ${formatearNumero(reporte.instagram_alcance || 0)}</div>
          <div>Clicks: ${formatearNumero(reporte.instagram_clicks || 0)}</div>
          <div>Msgs: ${formatearNumero(reporte.instagram_mensajes || 0)}</div>
          <div class="font-semibold">$${formatearNumero(igImporte)}</div>
        </div>
      </td>
      <td class="px-4 py-2 text-center">
        <div class="flex flex-col space-y-2">
          <a href="/panel_cliente/${document.body.dataset.nora}/meta_ads/reportes/descargar/${reporte.id}" 
             class="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm hover:bg-blue-200">
            Descargar
          </a>
          <button onclick="eliminarReporte('${reporte.id}')"
                  class="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200">
            Eliminar
          </button>
          <a href="/panel_cliente/${document.body.dataset.nora}/meta_ads/reportes/${reporte.id}" 
             class="inline-block px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm hover:bg-green-200">
            Ver Detalles
          </a>
        </div>
      </td>
    </tr>
  `}).join('');
}
// Formatea un número con separador de miles y decimales (ej: 1,234.56)
function formatearNumero(num) {
  if (isNaN(num)) return num;
  return Number(num).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatearFecha(fecha) {
  if (!fecha) return 'N/A';
  try {
    return new Date(fecha).toLocaleDateString('es-MX');
  } catch (e) {
    return fecha;
  }
}

async function cargarReportes() {
  const statusDiv = document.getElementById('reporte-status');
  const tbody = document.querySelector('.overflow-x-auto table tbody');
  
  if (statusDiv) statusDiv.textContent = 'Cargando reportes...';
  if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-blue-600">Cargando reportes...</td></tr>';

  try {
    const nombreNora = document.body.dataset.nora;
    console.log('[DEBUG] Cargando reportes para:', nombreNora);
    
    console.log('[DEBUG] Iniciando petición fetch');
    const url = `/panel_cliente/${nombreNora}/meta_ads/reportes`;
    console.log('[DEBUG] Haciendo fetch a URL:', url);
    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });
    
    if (!resp.ok) {
      console.error('[DEBUG] Error HTTP:', resp.status);
      throw new Error(`Error HTTP: ${resp.status}`);
    }
    
    const contentType = resp.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      console.error('[DEBUG] Tipo de contenido inválido:', contentType);
      throw new Error('La respuesta no es JSON válido');
    }
    
    const data = await resp.json();
    console.log('[DEBUG] Datos recibidos:', data);
    
    if (!data.ok) {
      throw new Error(data.error || 'Error desconocido');
    }

    renderizarReportes(data.reportes);
    if (statusDiv) statusDiv.textContent = '';

  } catch (error) {
    console.error('❌ Error cargando reportes:', error);
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-600">Error: ${error.message}</td></tr>`;
    }
    if (statusDiv) {
      statusDiv.textContent = 'Error cargando reportes: ' + error.message;
      statusDiv.className = 'mt-4 text-center text-lg text-red-600';
    }
  }
}

function formatearFecha(fecha) {
  if (!fecha) return 'N/A';
  try {
    return new Date(fecha).toLocaleDateString('es-MX');
  } catch (e) {
    return fecha;
  }
}

function inicializarEventosDescarga() {
  document.querySelectorAll('a[data-reporte-id]').forEach(link => {
    link.addEventListener('click', async function(e) {
      e.preventDefault();
      const reporteId = this.dataset.reporteId;
      const nombreNora = document.body.dataset.nora;
      window.location.href = `/panel_cliente/${nombreNora}/meta_ads/reportes/${reporteId}/descargar`;
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  console.log('🟢 [DEBUG] DOM Cargado, inicializando reportes_meta_ads.js');
  
  // Cargar reportes inmediatamente
  cargarReportes();

  // Inicializar botones
  const btnGenerar = document.getElementById('btn-generar-reporte');
  const btnEliminar = document.getElementById('btn-eliminar-reportes');
  const statusDiv = document.getElementById('reporte-status');

  // Botón generar reporte semanal
  if (btnGenerar) {
    btnGenerar.onclick = async function() {
      console.log('🔄 [DEBUG] Generando reporte semanal...');
      btnGenerar.disabled = true;
      statusDiv.textContent = 'Generando reporte semanal...';
      statusDiv.className = 'mt-4 text-center text-lg text-blue-600';

      try {
        const nombreNora = document.body.dataset.nora;
        const resp = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas`, { 
          method: 'POST',
          headers: {'Content-Type': 'application/json'}
        });
        const data = await resp.json();

        if (data.ok) {
          statusDiv.textContent = '✅ Reporte generado correctamente';
          statusDiv.className = 'mt-4 text-center text-lg text-green-600';
          await cargarReportes(); // Recargar la lista de reportes
        } else {
          throw new Error(data.error || 'Error desconocido');
        }
      } catch (error) {
        console.error('❌ Error:', error);
        statusDiv.textContent = 'Error generando reporte: ' + error.message;
        statusDiv.className = 'mt-4 text-center text-lg text-red-600';
      }

      btnGenerar.disabled = false;
    };
  }

  // Botón eliminar reportes
  if (btnEliminar) {
    btnEliminar.onclick = async function() {
      if (!confirm('¿Estás seguro de eliminar TODOS los reportes? Esta acción no se puede deshacer.')) {
        return;
      }

      btnEliminar.disabled = true;
      statusDiv.textContent = '🗑️ Eliminando reportes...';
      statusDiv.className = 'mt-4 text-center text-lg text-blue-600';

      try {
        const nombreNora = document.body.dataset.nora;
        const resp = await fetch(`/panel_cliente/${nombreNora}/meta_ads/estadisticas/eliminar_reportes`, {
          method: 'POST'
        });
        const data = await resp.json();

        if (data.ok) {
          statusDiv.textContent = `✅ Se eliminaron ${data.eliminados} reportes`;
          statusDiv.className = 'mt-4 text-center text-lg text-green-600';
          await cargarReportes(); // Recargar la lista
        } else {
          throw new Error(data.error || 'Error desconocido');
        }
      } catch (error) {
        console.error('❌ Error:', error);
        statusDiv.textContent = 'Error eliminando reportes: ' + error.message;
        statusDiv.className = 'mt-4 text-center text-lg text-red-600';
      }

      btnEliminar.disabled = false;
    };
  }

  console.log('✅ [DEBUG] Scripts de reportes Meta Ads inicializados');
});
