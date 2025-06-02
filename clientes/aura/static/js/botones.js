// ✅ Archivo: static/js/tareas_botones.js

window.abrirModalTarea = function () {
  const contenedor = document.getElementById("contenedorModalTarea");
  const modal = document.getElementById("modalTarea");
  const form = document.getElementById("formTarea");
  const boton = document.getElementById("btnNuevaTarea");

  if (contenedor && modal && form) {
    const abierto = !contenedor.classList.contains("max-h-0");

    contenedor.classList.toggle("max-h-0", abierto);
    contenedor.classList.toggle("max-h-[1000px]", !abierto);
    modal.classList.toggle("hidden", abierto);

    if (!abierto) {
      form.reset();
      const tareaIdInput = document.getElementById("tarea_id");
      if (tareaIdInput) tareaIdInput.value = "";
      document.getElementById("modalTitulo").textContent = "Nueva tarea";
    }

    if (boton) {
      boton.innerHTML = abierto ? "➕ Nueva tarea" : "✖️ Cerrar formulario";
    }
  }
};
