// Acciones de contactos: editar, eliminar, convertir a cliente

document.addEventListener("DOMContentLoaded", () => {
  // Editar contacto
  document.querySelectorAll('.btn-editar-contacto').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const row = btn.closest('tr');
      if (!row) return;
      // Extrae los datos del contacto de las celdas
      const telefono = row.querySelector('[data-campo="telefono"]').textContent.trim();
      const nombre = row.querySelector('[data-campo="nombre"]').textContent.trim();
      const correo = row.querySelector('[data-campo="correo"]').textContent.trim();
      const empresa = row.querySelector('[data-campo="empresa"]').textContent.trim();
      const rfc = row.querySelector('[data-campo="rfc"]')?.textContent.trim() || '';
      const direccion = row.querySelector('[data-campo="direccion"]')?.textContent.trim() || '';
      const ciudad = row.querySelector('[data-campo="ciudad"]').textContent.trim();
      const cumpleanos = row.querySelector('[data-campo="cumpleanos"]')?.textContent.trim() || '';
      const notas = row.querySelector('[data-campo="notas"]')?.textContent.trim() || '';
      // Llena el modal de nuevo contacto con los datos
      document.getElementById('telefono').value = telefono;
      document.getElementById('nombre').value = nombre;
      document.getElementById('correo').value = correo;
      document.getElementById('empresa').value = empresa;
      document.getElementById('rfc').value = rfc;
      document.getElementById('direccion').value = direccion;
      document.getElementById('ciudad').value = ciudad;
      document.getElementById('cumpleanos').value = cumpleanos;
      document.getElementById('notas').value = notas;
      // Abre el modal
      abrirModalContacto();
      // Cambia el texto y función del botón submit para modo edición
      const submitBtn = document.querySelector('#formNuevoContacto button[type="submit"]');
      if (submitBtn) {
        submitBtn.textContent = 'Guardar cambios';
        submitBtn.onclick = function(ev) {
          ev.preventDefault();
          // Recolecta los datos del formulario
          const form = document.getElementById('formNuevoContacto');
          const formData = new FormData(form);
          // El teléfono original debe ir en la URL
          fetch(`/panel_cliente/${document.body.dataset.nora}/contactos/editar/${telefono}`, {
            method: 'POST',
            body: formData
          }).then(resp => {
            if (resp.ok) {
              cerrarModalContacto();
              window.location.reload();
            } else {
              alert('Error al guardar cambios');
            }
          });
        };
      }
    });
  });

  // Eliminar contacto
  document.querySelectorAll('.btn-eliminar-contacto').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      if (!confirm('¿Seguro que deseas eliminar este contacto?')) return;
      const row = btn.closest('tr');
      const telefono = row.querySelector('[data-campo="telefono"]').textContent.trim();
      fetch(`/panel_cliente/${document.body.dataset.nora}/contactos/eliminar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telefono })
      }).then(resp => {
        if (resp.ok) {
          row.remove();
        } else {
          alert('Error al eliminar el contacto');
        }
      });
    });
  });

  // Convertir a cliente
  document.querySelectorAll('.btn-convertir-cliente').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const row = btn.closest('tr');
      const telefono = row.querySelector('[data-campo="telefono"]').textContent.trim();
      fetch(`/panel_cliente/${document.body.dataset.nora}/contactos/convertir_cliente`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telefono })
      }).then(resp => {
        if (resp.ok) {
          alert('Contacto convertido a cliente');
        } else {
          alert('Error al convertir a cliente');
        }
      });
    });
  });

  // Ver historial de conversaciones
  document.querySelectorAll('.btn-historial-contacto').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const telefono = btn.getAttribute('data-telefono');
      const nombre = btn.getAttribute('data-nombre') || '';
      const modal = document.getElementById('modalHistorialContacto');
      const loading = document.getElementById('historialLoading');
      const mensajesDiv = document.getElementById('historialMensajes');
      mensajesDiv.innerHTML = '';
      loading.classList.remove('hidden');
      modal.classList.remove('hidden');
      // Título dinámico
      modal.querySelector('h3').textContent = `🕑 Historial de ${nombre}`;
      // Fetch historial
      fetch(`/panel_cliente/${document.body.dataset.nora}/contactos/historial/${telefono}`)
        .then(resp => resp.json())
        .then(data => {
          loading.classList.add('hidden');
          if (data.mensajes && data.mensajes.length > 0) {
            mensajesDiv.innerHTML = data.mensajes.map(m => {
              const esCliente = m.emisor === 'cliente';
              return `
                <div class="flex ${esCliente ? 'justify-end' : 'justify-start'}">
                  <div class="max-w-[70%] px-4 py-2 rounded-2xl shadow-sm ${esCliente ? 'bg-blue-100 text-blue-900' : 'bg-white text-gray-800 border'}" style="word-break:break-word;">
                    <div class="text-xs text-gray-400 mb-1 flex items-center gap-1">
                      <span>${m.timestamp ? new Date(m.timestamp).toLocaleString() : ''}</span>
                      <span>${esCliente ? 'Tú' : (m.emisor || 'Nora')}</span>
                    </div>
                    <div class="font-normal leading-snug">${m.mensaje}</div>
                  </div>
                </div>
              `;
            }).join('');
            // Scroll al final
            setTimeout(() => { mensajesDiv.scrollTop = mensajesDiv.scrollHeight; }, 100);
          } else {
            mensajesDiv.innerHTML = '<div class="text-gray-400 text-center">Sin mensajes</div>';
          }
        })
        .catch(() => {
          loading.classList.add('hidden');
          mensajesDiv.innerHTML = '<div class="text-red-500 text-center">Error al cargar historial</div>';
        });
    });
  });

  // Cerrar modal historial
  document.getElementById('btnCerrarHistorial').onclick = cerrarModalHistorial;
  document.getElementById('btnCerrarHistorial2').onclick = cerrarModalHistorial;
  function cerrarModalHistorial() {
    document.getElementById('modalHistorialContacto').classList.add('hidden');
    document.getElementById('historialMensajes').innerHTML = '';
    document.getElementById('historialLoading').classList.add('hidden');
  }
});
