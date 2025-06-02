// Elimina legacy y deja solo el flujo para el modal de creación actual

document.addEventListener("DOMContentLoaded", () => {
  // Mostrar/ocultar campos de recurrencia en el modal de nueva tarea
  const recCheck = document.getElementById("recurrente_checkbox");
  const recFields = document.getElementById("recurrente_fields");
  if (recCheck && recFields) {
    recCheck.addEventListener("change", e => {
      recFields.classList.toggle("hidden", !e.target.checked);
    });
  }

  // Enviar formulario de creación de tarea
  const form = document.getElementById("formTareaCrear");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const payload = {};
    formData.forEach((val, key) => {
      if (val) payload[key] = val;
    });

    // Validaciones mínimas
    if (!payload.titulo) {
      alert("El título es obligatorio");
      return;
    }
    if (!payload.usuario_empresa_id) {
      alert("Debes asignar un responsable");
      return;
    }

    // Detectar Nora para la URL
    const nombreNora = form.querySelector('[name="nombre_nora"]').value;

    try {
      const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/crear`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (res.ok && (data.ok || data.id)) {
        location.reload();
      } else {
        alert("❌ " + (data.error || "Error al crear la tarea"));
      }
    } catch (err) {
      alert("❌ Error de red al crear la tarea");
      console.error(err);
    }
  });
});
document.addEventListener("DOMContentLoaded", function() {
  var btnCancelar = document.getElementById("btnCancelarTarea");
  if(btnCancelar) {
    btnCancelar.onclick = function() {
      document.getElementById("modalTarea").classList.add("hidden");
    }
  }
});

// ✅ Archivo: clientes/aura/static/js/tareas_modal_nueva.js

window.abrirModalTarea = function () {
  const contenedor = document.getElementById("contenedorModalTarea");
  const modal = document.getElementById("modalTarea");
  const form = document.getElementById("formTarea");
  const boton = document.getElementById("btnNuevaTarea");

  if (!contenedor || !modal || !form) return;

  const abierto = !contenedor.classList.contains("max-h-0");

  if (abierto) {
    contenedor.classList.add("max-h-0");
    contenedor.classList.remove("max-h-[1000px]");
    if (boton) boton.innerHTML = "➕ Nueva tarea";
  } else {
    contenedor.classList.remove("max-h-0");
    contenedor.classList.add("max-h-[1000px]");
    modal.classList.remove("hidden");
    form.reset();
    const tareaId = document.getElementById("tarea_id");
    if (tareaId) tareaId.value = "";
    document.getElementById("modalTitulo").textContent = "Nueva tarea";
    if (boton) boton.innerHTML = "✖️ Cerrar formulario";
  }
};

window.cerrarModalTarea = function () {
  document.getElementById("modalNuevaTarea").classList.add("hidden");
};