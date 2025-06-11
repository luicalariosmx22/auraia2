// ⚠️ Cambiar de export a función global

// import { postJSON } from "./tareas_utils.js";  // ❌ Elimina este import si no usas postJSON

console.log('[DEBUG] tareas_modal_ver.js cargado');

// ================== COMENTARIOS DE TAREA =====================
async function cargarComentariosTarea(tareaId, nombreNora) {
  const contenedor = document.getElementById("comentariosTarea");
  if (!contenedor) return;
  contenedor.innerHTML = '<div class="text-gray-400 text-xs">Cargando comentarios...</div>';
  try {
    const res = await fetch(`/panel_cliente/${nombreNora}/tareas/${tareaId}/comentarios`);
    // Si la respuesta no es ok, no mostrar error visual aquí, solo loguear para depuración
    if (!res.ok) {
      console.warn('Error al cargar comentarios:', res.status, await res.text());
      return;
    }
    const comentarios = await res.json();
    if (!Array.isArray(comentarios) || comentarios.length === 0) {
      contenedor.innerHTML = `<div class=\"flex flex-col items-center justify-center text-gray-500 text-xs py-2">
        <svg xmlns=\"http://www.w3.org/2000/svg" class=\"mx-auto mb-1\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 48 48\"><rect width=\"48\" height=\"48\" rx=\"12\" fill=\"#F3F4F6\"/><path d=\"M14 20a8 8 0 0 1 8-8h4a8 8 0 0 1 8 8v4a8 8 0 0 1-8 8h-2l-4 4v-4a8 8 0 0 1-8-8v-4z\" stroke=\"#A5B4FC\" stroke-width=\"2\" fill=\"#fff\"/><circle cx=\"20\" cy=\"24\" r=\"1.5\" fill=\"#A5B4FC\"/><circle cx=\"24\" cy=\"24\" r=\"1.5\" fill=\"#A5B4FC\"/><circle cx=\"28\" cy=\"24\" r=\"1.5\" fill=\"#A5B4FC\"/></svg>
        <span>Sin comentarios/actualizaciones.<br>Escribe el primero...</span>
      </div>`;
      return;
    }
    contenedor.innerHTML = comentarios.map(c => `
      <div class="border-b border-gray-200 pb-1 mb-1">
        <div class="flex items-center gap-2 text-xs text-gray-500">
          <span class="font-semibold text-gray-700">${c.usuario_nombre}</span>
          <span>${(c.created_at||c.fecha||'').replace('T',' ').slice(0,16)}</span>
        </div>
        <div class="text-gray-800 text-sm">${c.texto}</div>
      </div>
    `).join('');
  } catch (e) {
    contenedor.innerHTML = `<div class=\"flex flex-col items-center justify-center text-gray-500 text-xs py-2">
      <svg xmlns=\"http://www.w3.org/2000/svg" class=\"mx-auto mb-1\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 48 48\"><rect width=\"48\" height=\"48\" rx=\"12\" fill=\"#FEE2E2\"/><text x=\"24\" y=\"28\" text-anchor=\"middle\" font-size=\"18\" fill=\"#EF4444\">!</text></svg>
      <span>Error al cargar comentarios</span>
    </div>`;
  }
}

// Manejar envío de nuevo comentario
const formComentario = document.getElementById("formNuevoComentario");
if (formComentario) {
  formComentario.addEventListener("submit", async function(e) {
    e.preventDefault();
    const tareaId = document.getElementById("verIdTarea")?.value;
    const nombreNora = document.body.dataset.nora;
    const textarea = document.getElementById("nuevoComentario");
    const texto = textarea.value.trim();
    if (!texto) return;
    try {
      const res = await fetch(`/panel_cliente/${nombreNora}/tareas/${tareaId}/comentarios`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto })
      });
      const data = await res.json();
      if (data.ok) {
        textarea.value = "";
        cargarComentariosTarea(tareaId, nombreNora);
      } else {
        alert(data.error || "Error al guardar comentario");
      }
    } catch (err) {
      alert("Error inesperado al guardar comentario");
    }
  });
}

// ================== SUBTAREAS EN MODAL =====================
async function cargarSubtareasModal(tareaId, nombreNora) {
  const loading = document.getElementById('subtareasModalLoading');
  const lista = document.getElementById('subtareasModalLista');
  const vacio = document.getElementById('subtareasModalVacio');
  const error = document.getElementById('subtareasModalError');
  if (!lista) return;
  loading?.classList.remove('hidden');
  vacio?.classList.add('hidden');
  error?.classList.add('hidden');
  lista.innerHTML = '';
  try {
    const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/${tareaId}/subtareas`);
    if (!res.ok) throw new Error('Network');
    const subtareas = await res.json();
    loading?.classList.add('hidden');
    if (!Array.isArray(subtareas) || subtareas.length === 0) {
      vacio?.classList.remove('hidden');
      return;
    }
    lista.innerHTML = subtareas.map(s => `
      <div class="flex items-center gap-2 border-b border-gray-100 py-1 group">
        <input type="checkbox" ${s.estatus === 'completada' ? 'checked' : ''} disabled class="accent-blue-600">
        <span class="flex-1">${s.titulo}</span>
        <span class="text-xs text-gray-400">${s.empresa_nombre || ''}</span>
        <!-- Opcional: botón editar/marcar completada -->
      </div>
    `).join('');
  } catch (e) {
    loading?.classList.add('hidden');
    error?.classList.remove('hidden');
    lista.innerHTML = '';
  }
}

const formNuevaSubtareaModal = document.getElementById('formNuevaSubtareaModal');
if (formNuevaSubtareaModal) {
  formNuevaSubtareaModal.addEventListener('submit', async function(e) {
    e.preventDefault();
    const input = document.getElementById('inputNuevaSubtareaModal');
    const titulo = input.value.trim();
    console.debug('[DEBUG][modal-ver] Submit subtarea | input:', input, '| titulo:', titulo);
    if (!titulo) {
      console.warn('[DEBUG][modal-ver] Título vacío, no se envía la subtarea');
      return;
    }
    const tareaId = document.getElementById('verIdTarea')?.value;
    console.log('[DEBUG][modal-ver] verIdTarea:', tareaId);
    const nombreNora = document.body.dataset.nora;
    const usuario_empresa_id = document.getElementById('verAsignado')?.value;
    const empresa_id = document.getElementById('verEmpresa')?.value;
    // Puedes agregar aquí más campos opcionales si tu tabla subtareas los requiere
    console.debug('[DEBUG][modal-ver] usuario_empresa_id:', usuario_empresa_id, '| empresa_id:', empresa_id);
    if (!tareaId || !usuario_empresa_id) {
      console.warn('[DEBUG][modal-ver] tareaId o usuario_empresa_id faltante:', tareaId, usuario_empresa_id);
      return;
    }
    const creado_por = document.body.dataset.usuarioid || document.getElementById('verAsignado')?.value;
    // nombre_nora solo para la URL, NO en el payload
    const payload = {
      titulo,
      tarea_padre_id: tareaId,
      usuario_empresa_id,
      empresa_id,
      creado_por
      // No enviar nombre_nora aquí
    };
    console.log('[DEBUG][modal-ver] payload a enviar:', payload);
    try {
      const resp = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/crear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      console.debug('[DEBUG][modal-ver] HTTP status:', resp.status);
      let data = null;
      try {
        data = await resp.json();
        console.debug('[DEBUG][modal-ver] Respuesta JSON backend:', data);
      } catch (jsonErr) {
        console.error('[DEBUG][modal-ver] Error parseando JSON:', jsonErr);
        const text = await resp.text();
        console.error('[DEBUG][modal-ver] Respuesta RAW:', text);
        alert('Respuesta no válida del backend');
        return;
      }
      if (data.ok) {
        input.value = '';
        console.info('[DEBUG][modal-ver] Subtarea creada correctamente, recargando lista de subtareas');
        await cargarSubtareasModal(tareaId, nombreNora);
        // No cerrar el modal ni recargar la página aquí
      } else {
        console.warn('[DEBUG][modal-ver] Error backend:', data.error);
        alert(data.error || 'Error al crear subtarea');
      }
    } catch (err) {
      console.error('[DEBUG][modal-ver] Error de red o JS:', err);
      alert('Error de red al crear subtarea');
    }
  });
}

// --- Agregar tarea existente como subtarea ---
document.addEventListener("DOMContentLoaded", function() {
  const formAgregar = document.getElementById("formAgregarSubtareaExistente");
  if (formAgregar) {
    formAgregar.addEventListener("submit", async function(e) {
      e.preventDefault();
      const input = document.getElementById("inputBuscarTareaExistente");
      const datalist = document.getElementById("datalistTareasDisponibles");
      const nombreNora = document.body.dataset.nora;
      const tareaPadreId = document.getElementById("verIdTarea")?.value;
      let tareaIdSeleccionada = null;
      // Buscar el id de la tarea seleccionada por título
      const valor = input.value.trim();
      if (!valor) return alert("Selecciona una tarea válida");
      for (const opt of datalist.options) {
        if (opt.value === valor) {
          tareaIdSeleccionada = opt.getAttribute("data-id");
          break;
        }
      }
      if (!tareaIdSeleccionada) return alert("Selecciona una tarea válida del listado");
      // Actualizar tarea seleccionada para que sea subtarea de la actual
      try {
        console.log('[DEBUG][subtarea] Enviando petición para convertir tarea en subtarea:', {
          tarea_id: tareaIdSeleccionada,
          tarea_padre_id: tareaPadreId
        });
        const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/convertir_en_subtarea`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tarea_id: tareaIdSeleccionada, tarea_padre_id: tareaPadreId })
        });
        if (!res.ok) {
          const text = await res.text();
          console.error('[DEBUG][subtarea] Error HTTP:', res.status, text);
          alert(`Error HTTP ${res.status}: ${text}`);
          return;
        }
        const data = await res.json();
        if (data.ok) {
          input.value = "";
          // Siempre recargar la lista de subtareas, nunca recargar la página ni cerrar el modal
          await cargarSubtareasModal(tareaPadreId, nombreNora);
          // Opcional: mostrar mensaje de éxito temporal
          // const msg = document.getElementById('msgSubtareaExistente');
          // if (msg) { msg.textContent = 'Subtarea agregada'; setTimeout(() => { msg.textContent = ''; }, 1500); }
        } else {
          alert(data.error || "Error al convertir en subtarea");
        }
      } catch (err) {
        console.error('[DEBUG][subtarea] Error de red o JS:', err);
        alert("Error de red al convertir en subtarea");
      }
    });
  }
});

// Hook para cargar comentarios y subtareas al abrir modal
window.initModalVerTareaListeners = function () {
  console.log('[DEBUG] Ejecutando initModalVerTareaListeners');
  document.querySelectorAll('.btn-ver-tarea').forEach((btn) => {
    // Eliminar listeners previos clonando el nodo
    const nuevoBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(nuevoBtn, btn);
    nuevoBtn.addEventListener('click', async () => {
      const tareaId = nuevoBtn.getAttribute("data-id");
      const nombreNora = nuevoBtn.getAttribute("data-nora");
      // Refuerzo: limpiar input y datalist antes de poblar
      const inputBuscar = document.getElementById("inputBuscarTareaExistente");
      if (inputBuscar) inputBuscar.value = "";
      const datalist = document.getElementById("datalistTareasDisponibles");
      if (datalist) datalist.innerHTML = "";
      let tarea = null;
      try {
        // Usar la nueva ruta que trae todo el contexto para el modal
        let res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/obtener_modal/${tareaId}`);
        if (!res.ok) {
          alert("❌ No se pudo cargar la información");
          return;
        }
        const data = await res.json();
        tarea = data.tarea;
        const tarea_padre = data.tarea_padre;
        const tareas_principales = data.tareas_principales || [];
        const subtareas = data.subtareas || [];

        // Mostrar modal
        const modal = document.getElementById("modalTarea");
        if (modal) modal.classList.remove("hidden");
        const tituloModal = document.getElementById("modalTitulo");
        if (tituloModal) tituloModal.textContent = "Ver / Editar tarea";

        // Asignar valores a los campos del modal
        const campos = {
          "verIdTarea": tarea.id,
          "verTitulo": tarea.titulo,
          "verDescripcion": tarea.descripcion,
          "verPrioridad": tarea.prioridad || "media",
          "verFechaLimite": tarea.fecha_limite
        };
        Object.entries(campos).forEach(([id, valor]) => {
          const el = document.getElementById(id);
          if (el) el.value = valor || "";
        });
        // Asignado y empresa
        const verAsignado = document.getElementById("verAsignado");
        if (verAsignado) {
          [...verAsignado.options].forEach(opt => {
            opt.selected = opt.value === (tarea.usuario_empresa_id || "");
          });
        }
        const verEmpresa = document.getElementById("verEmpresa");
        if (verEmpresa) {
          [...verEmpresa.options].forEach(opt => {
            opt.selected = opt.value === (tarea.empresa_id || "");
          });
        }
        // Select de tarea padre
        const selectPadre = document.getElementById("verTareaPadre");
        if (selectPadre) {
          // Limpiar y poblar opciones
          selectPadre.innerHTML = '<option value="">— Ninguna (tarea principal) —</option>';
          tareas_principales.forEach(t => {
            if (t.id !== tarea.id) {
              const opt = document.createElement('option');
              opt.value = t.id;
              opt.textContent = t.titulo + (t.empresa_nombre ? ` — ${t.empresa_nombre}` : '');
              if (tarea_padre && tarea_padre.id === t.id) opt.selected = true;
              selectPadre.appendChild(opt);
            }
          });
        }
        // Recurrencia
        const chkRecurrente = document.getElementById("verEsRecurrente");
        const hiddenRecurrente = document.getElementById("verIsRecurrente");
        const camposRecurrente = document.getElementById("verCamposRecurrente");
        if (chkRecurrente && hiddenRecurrente && camposRecurrente) {
          chkRecurrente.checked = tarea.is_recurrente === true || tarea.is_recurrente === 'true';
          if (chkRecurrente.checked) {
            camposRecurrente.classList.remove("hidden");
            hiddenRecurrente.value = "true";
          } else {
            camposRecurrente.classList.add("hidden");
            hiddenRecurrente.value = "false";
          }
        }
        // --- Poblar datalist de tareas disponibles para subtarea ---
        const tareasDisponibles = data.tareas_disponibles_para_subtarea || [];
        const datalist = document.getElementById("datalistTareasDisponibles");
        if (datalist) {
          datalist.innerHTML = "";
          tareasDisponibles.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t.titulo;
            opt.setAttribute("data-id", t.id);
            opt.textContent = t.titulo + (t.empresa_nombre ? ` — ${t.empresa_nombre}` : "");
            datalist.appendChild(opt);
          });
        }

        cargarComentariosTarea(tareaId, nombreNora);
        cargarSubtareasModal(tareaId, nombreNora);
      } catch (error) {
        console.error(error);
        alert("❌ No se pudo cargar la información");
      }
    });
  });

  // Guardar cambios de tarea
  const form = document.getElementById('formVerTarea');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const tareaId = document.getElementById("verIdTarea")?.value;
      const nombreNora = document.body.dataset.nora;
      const hiddenRecurrenteEl = document.getElementById("verIsRecurrente");
      const usuarioAsignado = document.getElementById("verAsignado")?.value;
      if (!usuarioAsignado || usuarioAsignado === "None" || usuarioAsignado === "none") {
        const alertContainer = document.getElementById("alertaGuardado");
        if (alertContainer) {
          alertContainer.innerText = "Debes seleccionar un usuario asignado válido.";
          alertContainer.classList.remove("d-none");
          alertContainer.classList.remove("alert-success");
          alertContainer.classList.add("alert", "alert-danger");
        } else {
          alert("Debes seleccionar un usuario asignado válido.");
        }
        return;
      }
      // Nuevo: tarea padre
      const tareaPadreId = document.getElementById("verTareaPadre")?.value || null;
      console.log('[DEBUG][modal] tareaId:', tareaId, '| tareaPadreId:', tareaPadreId);
      const payload = {
        titulo: document.getElementById("verTitulo")?.value,
        descripcion: document.getElementById("verDescripcion")?.value,
        prioridad: document.getElementById("verPrioridad")?.value,
        estatus: document.getElementById("verEstatus")?.value,
        fecha_limite: document.getElementById("verFechaLimite")?.value,
        usuario_empresa_id: usuarioAsignado,
        empresa_id: document.getElementById("verEmpresa")?.value,
        is_recurrente: hiddenRecurrenteEl ? hiddenRecurrenteEl.value : "false",
        dtstart: document.getElementById("verDtstart")?.value,
        rrule: document.getElementById("verRrule")?.value,
        until: document.getElementById("verUntil")?.value,
        count: document.getElementById("verCount")?.value
        // tarea_padre_id: tareaPadreId // ← No enviar este campo al actualizar tarea normal
      };
      // Eliminar tarea_padre_id y campos de recurrencia del payload si existen (solo se deben enviar en creación)
      const camposPermitidos = [
        'titulo',
        'prioridad',
        'fecha_limite',
        'estatus',
        'usuario_empresa_id',
        'empresa_id',
        'descripcion'
      ];
      Object.keys(payload).forEach(k => {
        if (!camposPermitidos.includes(k)) {
          delete payload[k];
        }
      });
      console.log('[DEBUG][modal] payload a enviar:', payload);
      const alertContainer = document.getElementById("alertaGuardado");
      if (!alertContainer) return;
      alertContainer.classList.add("d-none");
      alertContainer.classList.remove("alert-success", "alert-danger");
      alertContainer.innerText = "";
      try {
        // Usar endpoint de actualización inline para cada campo
        let errores = [];
        for (const [campo, valor] of Object.entries(payload)) {
          console.log(`[DEBUG][modal] Enviando update campo: ${campo} | valor:`, valor);
          if (typeof valor === 'undefined') continue;
          if (valor !== null && valor !== '') { // Solo enviar campos válidos
            const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/actualizar/${tareaId}`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ campo, valor })
            });
            const resultado = await res.json();
            console.log(`[DEBUG][modal] Respuesta backend para campo ${campo}:`, resultado);
            if (!resultado.ok) {
              errores.push(resultado.error || `Error al actualizar ${campo}`);
            }
          }
        }
        if (errores.length === 0) {
          alertContainer.innerText = "✅ Cambios guardados correctamente";
          alertContainer.classList.remove("d-none");
          alertContainer.classList.add("alert", "alert-success");
          // --- NUEVO: cerrar modal y recargar para ver cambios ---
          setTimeout(() => {
            document.getElementById("modalTarea")?.classList.add("hidden");
            window.location.reload();
          }, 600);
        } else {
          alertContainer.innerText = "❌ Error: " + errores.join("; ");
          alertContainer.classList.remove("d-none");
          alertContainer.classList.add("alert", "alert-danger");
        }
      } catch (error) {
        console.error(error);
        alertContainer.innerText = "❌ Error inesperado al guardar los cambios";
        alertContainer.classList.remove("d-none");
        alertContainer.classList.add("alert", "alert-danger");
      }
    });
  }
};

// Ejecutar automáticamente al cargar el DOM
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", window.initModalVerTareaListeners);
} else {
  window.initModalVerTareaListeners();
}
