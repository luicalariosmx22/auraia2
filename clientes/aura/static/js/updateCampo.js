// ✅ Archivo: static/js/updateCampo.js

// Maneja actualizaciones inline de campos en la tabla de tareas
// Incluye: estatus (checkbox), empresa, asignado, fecha, prioridad, autocompletado y modal editar

// ✅ Actualizar un campo inline
window.updateCampo = async function (elemento, campo, valorManual = null) {
  if (campo === "empresa_id") return;  // 🚫 No permitir actualizar empresa después de creada

  const fila = elemento.closest("tr");
  const tareaId = fila.getAttribute("data-id");
  const nombreNora = document.body.dataset.nombreNora;
  const valor = valorManual !== null ? valorManual : (elemento.type === "checkbox" ? (elemento.checked ? "completada" : "pendiente") : elemento.value);

  try {
    const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/actualizar/${tareaId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ campo, valor })
    });
    const data = await res.json();
    if (data.ok) console.log("✅ Campo actualizado correctamente");
    else console.warn("⚠️ Error en actualización:", data);
  } catch (err) {
    console.error("❌ Error de red en updateCampo:", err);
  }
};

// ✅ Checkbox estatus (completada / pendiente)
window.toggleEstatus = function (checkbox) {
  window.updateCampo(checkbox, "estatus").then(() => location.reload());
};

// ✅ Autocompletar campos con datalist (asignado)
window.handleAutoCompleteInput = function (input, campo) {
  if (campo === "empresa_id") return;

  const val = input.value.trim();
  const datalistId = input.getAttribute("list");
  const options = document.querySelectorAll(`#${datalistId} option`);
  let id = null;
  options.forEach(opt => {
    if (opt.value === val) id = opt.getAttribute("data-id");
  });
  if (!id) {
    return;
  }
  window.updateCampo(input, campo, id).then(() => location.reload());
};

// window.cargarTareaEnModal = async function (boton) {
//   const tareaId = boton.getAttribute("data-id");
//   const nombreNora = boton.getAttribute("data-nora");
//
//   try {
//     const res = await fetch(`/panel_cliente/${nombreNora}/tareas/obtener/${tareaId}`);
//     const tarea = await res.json();
//     if (!tarea || tarea.error) return alert("❌ Error al cargar la tarea");
//     // Mostrar modal
//     document.getElementById("modalTarea")?.classList.remove("hidden");
//     document.getElementById("modalTitulo").textContent = "Editar tarea";
//
//     // Rellenar campos usando IDs únicos del modal editar
//     document.getElementById("verIdTarea").value = tarea.id || "";
//     document.getElementById("verTitulo").value = tarea.titulo || "";
//     document.getElementById("verDescripcion").value = tarea.descripcion || "";
//     document.getElementById("verPrioridad").value = tarea.prioridad || "media";
//     document.getElementById("verFechaLimite").value = tarea.fecha_limite || "";
//     document.getElementById("verEstatus").value = tarea.estatus || "pendiente";
//
//     if (document.getElementById("verAsignado")) {
//       document.getElementById("verAsignado").value = tarea.usuario_empresa_id || "";
//     }
//     if (document.getElementById("verEmpresa")) {
//       document.getElementById("verEmpresa").value = tarea.empresa_id || "";
//     }
//
//   } catch (err) {
//     console.error("❌ No se pudo cargar la tarea:", err);
//   }
// };

// ✅ Eliminar tarea desde botón
window.eliminarTarea = function (id) {
  const nombreNora = document.body.dataset.nombreNora;
  if (confirm("¿Eliminar esta tarea?")) {
    fetch(`/panel_cliente/${nombreNora}/tareas/eliminar/${id}`, {
      method: "POST"
    }).then(() => location.reload());
  }
};

// ✅ Manejar envío del formulario modal de tarea (crear/editar)
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formTarea");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const tareaId = document.getElementById("tarea_id").value;
    const nombreNora = document.body.dataset.nombreNora;

    const payload = {
      titulo: document.getElementById("titulo").value,
      descripcion: document.getElementById("descripcion").value,
      prioridad: document.getElementById("prioridad").value,
      fecha_limite: document.getElementById("fecha_limite").value,
      estatus: document.getElementById("estatus").value,
      usuario_empresa_id: document.getElementById("usuario_empresa_id").value,
      empresa_id: document.getElementById("empresa_id").value
    };

    try {
      const res = await fetch(`/panel_cliente/${nombreNora}/tareas/actualizar/${tareaId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (data.ok) {
        document.getElementById("modalTarea").classList.add("hidden");
        location.reload();
      } else {
        console.warn(data);
      }
    } catch (err) {
      console.error("❌ Error al actualizar la tarea", err);
    }
  });
});

