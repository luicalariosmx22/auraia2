// ⚠️ Cambiar de export a función global

// import { postJSON } from "./tareas_utils.js";  // ❌ Elimina este import si no usas postJSON

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
        <svg xmlns=\"http://www.w3.org/2000/svg\" class=\"mx-auto mb-1\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 48 48\"><rect width=\"48\" height=\"48\" rx=\"12\" fill=\"#F3F4F6\"/><path d=\"M14 20a8 8 0 0 1 8-8h4a8 8 0 0 1 8 8v4a8 8 0 0 1-8 8h-2l-4 4v-4a8 8 0 0 1-8-8v-4z\" stroke=\"#A5B4FC\" stroke-width=\"2\" fill=\"#fff\"/><circle cx=\"20\" cy=\"24\" r=\"1.5\" fill=\"#A5B4FC\"/><circle cx=\"24\" cy=\"24\" r=\"1.5\" fill=\"#A5B4FC\"/><circle cx=\"28\" cy=\"24\" r=\"1.5\" fill=\"#A5B4FC\"/></svg>
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
      <svg xmlns=\"http://www.w3.org/2000/svg\" class=\"mx-auto mb-1\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 48 48\"><rect width=\"48\" height=\"48\" rx=\"12\" fill=\"#FEE2E2\"/><text x=\"24\" y=\"28\" text-anchor=\"middle\" font-size=\"18\" fill=\"#EF4444\">!</text></svg>
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

// Hook para cargar comentarios al abrir modal
window.initModalVerTareaListeners = function () {
  document.querySelectorAll(".btn-ver-tarea").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const tareaId = btn.getAttribute("data-id");
      const nombreNora = btn.getAttribute("data-nora");

      try {
        const res = await fetch(`/panel_cliente/${nombreNora}/tareas/obtener/${tareaId}`);
        if (!res.ok) {
          alert("❌ No se pudo cargar la información");
          return;
        }
        const tarea = await res.json();

        if (tarea.error) {
          alert("❌ Error al cargar la tarea: " + tarea.error);
          return;
        }

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

        const verAsignado = document.getElementById("verAsignado");
        if (verAsignado) {
          if (verAsignado.tagName === "SELECT") {
            [...verAsignado.options].forEach(opt => {
              opt.selected = opt.value === (tarea.usuario_empresa_id || "");
            });
          } else {
            verAsignado.value = tarea.asignado_nombre || "";
          }
        }

        const verEmpresa = document.getElementById("verEmpresa");
        if (verEmpresa) {
          if (verEmpresa.tagName === "SELECT") {
            [...verEmpresa.options].forEach(opt => {
              opt.selected = opt.value === (tarea.empresa_id || "");
            });
          } else {
            verEmpresa.value = tarea.empresa_nombre || "";
          }
        }

        // --- Recurrencia: mostrar/ocultar campos y normalizar valor ---
        const chkRecurrente = document.getElementById("verEsRecurrente");
        const hiddenRecurrente = document.getElementById("verIsRecurrente");
        const camposRecurrente = document.getElementById("verCamposRecurrente");

        if (chkRecurrente && hiddenRecurrente && camposRecurrente) {
          // Mostrar/ocultar campos según el checkbox
          chkRecurrente.addEventListener("change", function () {
            if (chkRecurrente.checked) {
              camposRecurrente.classList.remove("hidden");
              hiddenRecurrente.value = "true";
            } else {
              camposRecurrente.classList.add("hidden");
              hiddenRecurrente.value = "false";
            }
          });
          // Al abrir modal: setear estado según datos existentes
          if (chkRecurrente.checked) {
            camposRecurrente.classList.remove("hidden");
            hiddenRecurrente.value = "true";
          } else {
            camposRecurrente.classList.add("hidden");
            hiddenRecurrente.value = "false";
          }
        }

        cargarComentariosTarea(tareaId, nombreNora);

      } catch (error) {
        console.error(error);
        alert("❌ No se pudo cargar la información");
      }
    });
  });

  // Guardar cambios de tarea
  const form = document.getElementById("formVerTarea");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const tareaId = document.getElementById("verIdTarea")?.value;
      const nombreNora = document.body.dataset.nora;
      const hiddenRecurrenteEl = document.getElementById("verIsRecurrente");

      // Validación usuario asignado
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
      };

      const alertContainer = document.getElementById("alertaGuardado");
      if (!alertContainer) return;

      alertContainer.classList.add("d-none");
      alertContainer.classList.remove("alert-success", "alert-danger");
      alertContainer.innerText = "";

      try {
        const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/actualizar_completa/${tareaId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        // Log de depuración: mostrar status y respuesta cruda
        console.log("[Depuración] Respuesta backend (status):", res.status);
        let resultadoRaw = await res.text();
        console.log("[Depuración] Respuesta backend (raw):", resultadoRaw);
        let resultado;
        try {
          resultado = JSON.parse(resultadoRaw);
        } catch (e) {
          resultado = { ok: false, error: "Respuesta no es JSON válido", raw: resultadoRaw };
        }

        if (resultado.ok) {
          alertContainer.innerText = "✅ Cambios guardados correctamente";
          alertContainer.classList.remove("d-none");
          alertContainer.classList.add("alert", "alert-success");
        } else {
          alertContainer.innerText = "❌ Error: " + (resultado.error || resultado.raw || "Error desconocido");
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
