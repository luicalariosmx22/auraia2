// ✅ Archivo: static/js/tareas_inline.js
// 🔁 Las funciones de updateCampo y handleAutoCompleteInput ahora están en: static/js/updateCampo.js
// Este archivo contiene solo utilidades de UI, inserción en tabla y notificaciones.

function mostrarNotificacion(mensaje) {
  const alerta = document.createElement("div");
  alerta.className = "fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded shadow text-sm z-50";
  alerta.textContent = mensaje;
  document.body.appendChild(alerta);
  setTimeout(() => alerta.remove(), 3000);
}

function insertarTareaEnTabla(tarea) {
  if (!tarea || !tarea.id) return;

  const tabla = document.getElementById("tablaTareas");
  if (!tabla) return;

  const row = document.createElement("tr");
  row.setAttribute("data-id", tarea.id);
  row.classList.add("hover:bg-gray-50");

  row.innerHTML = `
    <td class="px-4 py-2 text-xs text-gray-500">${tarea.codigo_tarea}</td>
    <td class="px-4 py-2 font-medium text-gray-700">${tarea.titulo}</td>
    <td class="px-4 py-2 text-sm">${tarea.prioridad}</td>
    <td class="px-4 py-2 text-sm">${tarea.fecha_limite || "-"}</td>
    <td class="px-4 py-2 text-sm">${tarea.estatus}</td>
    <td class="px-4 py-2 text-sm">—</td>
    <td class="px-4 py-2 text-sm text-right">
      <button class="btn-ver-tarea text-blue-600 text-sm" data-id="${tarea.id}" data-nora="${tarea.nombre_nora}">Ver</button>
    </td>
  `;

  tabla.querySelector("tbody").prepend(row);
}

// Aquí puedes agregar otras utilidades de UI o modales, pero no lógica de actualización directa de campos.

