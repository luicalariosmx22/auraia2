// Archivo: clientes/aura/static/js/reportes_meta_ads.js

// Formatea un número con separador de miles y decimales (ej: 1,234.56)
function formatearNumero(num) {
  if (isNaN(num)) return num;
  return Number(num).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Lógica para el botón Generar/Actualizar Reporte Meta Ads

document.addEventListener('DOMContentLoaded', function() {
  const btnGenerar = document.getElementById('btn-generar-reporte');
  const statusDiv = document.getElementById('reporte-status');

  if (btnGenerar) {
    btnGenerar.onclick = async function() {
      btnGenerar.disabled = true;
      statusDiv.textContent = 'Generando reporte...';
      statusDiv.className = 'mt-4 text-center text-lg text-blue-600';
      try {
        // Extrae el nombre_nora del HTML (puedes ajustar si lo tienes en otro lado)
        let nombreNora = document.body.dataset.nora;
        if (!nombreNora) {
          // Busca en la URL si no está en el body
          const match = window.location.pathname.match(/panel_cliente\/(.*?)\//);
          nombreNora = match ? match[1] : '';
        }
        // Obtener el cuenta_id de un input/select
        const cuentaId = document.getElementById('select-cuenta-id')?.value || '';
        if (!cuentaId) {
          statusDiv.textContent = 'Selecciona una cuenta publicitaria.';
          statusDiv.className = 'mt-4 text-center text-lg text-red-600';
          btnGenerar.disabled = false;
          return;
        }
        const url = `/panel_cliente/${nombreNora}/meta_ads/estadisticas`;
        const resp = await fetch(url, { 
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ cuenta_id: cuentaId })
        });
        if (!resp.ok) {
          console.error(`[ERROR] HTTP ${resp.status} al hacer POST a ${url}`);
          statusDiv.textContent = `Error generando reporte: HTTP ${resp.status} (${resp.statusText})`;
          statusDiv.className = 'mt-4 text-center text-lg text-red-600';
          btnGenerar.disabled = false;
          return;
        }
        let data;
        try {
          data = await resp.json();
        } catch (e) {
          console.error('[ERROR] Respuesta no válida del servidor (no es JSON):', e, resp);
          statusDiv.textContent = 'Error generando reporte: respuesta no válida del servidor';
          statusDiv.className = 'mt-4 text-center text-lg text-red-600';
          btnGenerar.disabled = false;
          return;
        }
        if (data.ok) {
          statusDiv.textContent = '✅ Reporte generado correctamente';
          statusDiv.className = 'mt-4 text-center text-lg text-green-600';
          // Opcional: recarga la página para ver el nuevo reporte
          setTimeout(() => window.location.reload(), 1200);
        } else {
          console.error('[ERROR] Respuesta JSON recibida pero con error:', data);
          throw new Error(data.error || 'Error desconocido');
        }
      } catch (error) {
        statusDiv.textContent = 'Error generando reporte: ' + error.message;
        statusDiv.className = 'mt-4 text-center text-lg text-red-600';
      }
      btnGenerar.disabled = false;
    };
  }
});
