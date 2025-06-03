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

        document.getElementById("modalTarea").classList.remove("hidden");
        document.getElementById("modalTitulo").textContent = "Ver / Editar tarea";

        // Asignar valores al modal
        document.getElementById("tarea_id").value = tarea.id || "";
        document.getElementById("verTitulo").value = tarea.titulo || "";
        document.getElementById("verDescripcion").value = tarea.descripcion || "";
        document.getElementById("verPrioridad").value = tarea.prioridad || "media";
        document.getElementById("verFechaLimite").value = tarea.fecha_limite || "";

        const verAsignado = document.getElementById("verAsignado");
        if (verAsignado.tagName === "SELECT") {
          [...verAsignado.options].forEach(opt => {
            opt.selected = opt.value === (tarea.usuario_empresa_id || "");
          });
        } else {
          verAsignado.value = tarea.asignado_nombre || "";
        }

        const verEmpresa = document.getElementById("verEmpresa");
        if (verEmpresa.tagName === "SELECT") {
          [...verEmpresa.options].forEach(opt => {
            opt.selected = opt.value === (tarea.empresa_id || "");
          });
        } else {
          verEmpresa.value = tarea.empresa_nombre || "";
        }

      } catch (error) {
        console.error(error);
        alert("❌ No se pudo cargar la información");
      }
    });
  });

  // Guardar cambios de tarea
  document.getElementById("formVerTarea").addEventListener("submit", async (e) => {
    e.preventDefault();

    const tareaId = document.getElementById("verIdTarea").value;
    const nombreNora = document.body.dataset.nora;

    const payload = {
      titulo: document.getElementById("verTitulo").value,
      descripcion: document.getElementById("verDescripcion").value,
      prioridad: document.getElementById("verPrioridad").value,
      estatus: document.getElementById("verEstatus").value,
      fecha_limite: document.getElementById("verFechaLimite").value,
      usuario_empresa_id: document.getElementById("verAsignado").value,
      empresa_id: document.getElementById("verEmpresa").value
    };

    const alertContainer = document.getElementById("alertaGuardado");
    alertContainer.classList.add("d-none");
    alertContainer.classList.remove("alert-success", "alert-danger");
    alertContainer.innerText = "";

    try {
      const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/actualizar/${tareaId}`, {
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
