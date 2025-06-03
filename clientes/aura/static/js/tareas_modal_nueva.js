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

  // Nuevo flujo para el modal de creación de tarea
  const formNueva = document.getElementById("formTareaNueva");
  if (formNueva) {
    formNueva.addEventListener("submit", async function (e) {
      e.preventDefault();

      const form = e.target;
      const datos = new FormData(form);
      const jsonData = Object.fromEntries(datos.entries());
      const nombreNora = jsonData.nombre_nora;

      try {
        const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/crear`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(jsonData)
        });

        const resultado = await res.json();
        if (resultado.ok || resultado.id) {
          alert("✅ Tarea guardada exitosamente");
          cerrarModalTarea();
          location.reload();
        } else {
          alert("❌ Error: " + (resultado.error || "No se pudo crear la tarea"));
        }
      } catch (err) {
        console.error(err);
        alert("❌ Error inesperado al guardar la tarea");
      }
    });
  }
});

document.addEventListener("DOMContentLoaded", function() {
  var btnCancelar = document.getElementById("btnCancelarTarea");
  if(btnCancelar) {
    btnCancelar.onclick = function() {
      document.getElementById("modalTarea").classList.add("hidden");
    }
  }
});


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