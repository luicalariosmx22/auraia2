// ✅ Archivo: static/js/tareas_botones.js

// ✅ Mostrar modal para crear nueva tarea
window.abrirModalTarea = function () {
  const modal = document.getElementById("modalNuevaTarea");
  if (modal) {
    modal.classList.remove("hidden");
  }
};

// ✅ Cerrar modal
window.cerrarModalTarea = function () {
  const modal = document.getElementById("modalNuevaTarea");
  if (modal) {
    modal.classList.add("hidden");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const boton = document.getElementById("btnNuevaTarea");
  if (boton) boton.addEventListener("click", abrirModalTarea);
});
