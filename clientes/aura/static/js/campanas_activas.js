// Archivo: static/js/campanas_activas.js

async function cargarAnuncios() {
  const nora = document.body.dataset.nora;
  const cuenta = document.body.dataset.cuenta;
  const loader = document.getElementById('loader');
  const tabla = document.getElementById('tablaAnuncios');
  const tbody = tabla.querySelector('tbody');
  const empty = document.getElementById('emptyState');
  const lastUpdate = document.getElementById('lastUpdate');

  loader.style.display = '';
  tabla.classList.add('hidden');
  empty.classList.add('hidden');
  tbody.innerHTML = '';

  let url = `/panel_cliente/${nora}/meta_ads/anuncios_activos_json?cuenta_id=${encodeURIComponent(cuenta)}`;

  try {
    const resp = await fetch(url);
    const data = await resp.json();
    if (!data.anuncios || !data.anuncios.length) {
      loader.style.display = 'none';
      empty.classList.remove('hidden');
      lastUpdate.textContent = '';
      window._setAnunciosActivos([]);
      return;
    }
    window._setAnunciosActivos(data.anuncios);
    loader.style.display = 'none';
    tabla.classList.remove('hidden');
    lastUpdate.textContent = 'Actualizado: ' + new Date().toLocaleTimeString();
  } catch (e) {
    loader.textContent = 'Error al cargar anuncios.';
    lastUpdate.textContent = '';
  }
}

// Si quieres usar el SDK de Facebook JS (FB.api), sería así:
// FB.api(
//   '/act_' + cuenta + '/ads',
//   'GET',
//   { fields: 'id,name,status,adset,preview_shareable_link,campaign', access_token: 'TU_TOKEN' },
//   function(response) {
//     if (response && !response.error) {
//       window._setAnunciosActivos(response.data);
//     } else {
//       loader.textContent = 'Error al cargar anuncios.';
//     }
//   }
// );
//
// Pero en tu flujo actual, el backend ya hace la consulta y el JS solo consume el JSON del backend.
// Si algún día quieres hacerlo directo desde el frontend, puedes usar el bloque de arriba.

document.getElementById('btnRefresh').onclick = cargarAnuncios;
document.addEventListener('DOMContentLoaded', cargarAnuncios);
