// ⚠️ Cambiar de export a función global

// import { postJSON } from "./tareas_utils.js";  // ❌ Elimina este import si no usas postJSON

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

      // 🟢 Obtén el input hidden directamente para evitar ReferenceError
      const hiddenRecurrenteEl = document.getElementById("verIsRecurrente");

      const payload = {
        titulo: document.getElementById("verTitulo")?.value,
        descripcion: document.getElementById("verDescripcion")?.value,
        prioridad: document.getElementById("verPrioridad")?.value,
        estatus: document.getElementById("verEstatus")?.value,
        fecha_limite: document.getElementById("verFechaLimite")?.value,
        usuario_empresa_id: document.getElementById("verAsignado")?.value,
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

        const resultado = await res.json();
        if (resultado.ok) {
          alertContainer.innerText = "✅ Cambios guardados correctamente";
          alertContainer.classList.remove("d-none");
          alertContainer.classList.add("alert", "alert-success");
        } else {
          alertContainer.innerText = "❌ Error: " + resultado.error;
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
