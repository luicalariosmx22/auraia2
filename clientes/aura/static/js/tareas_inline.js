import { postJSON } from "./tareas_utils.js";

export async function updateField(id, campo, valor, nombreNora) {
  const url = `/panel_cliente/${nombreNora}/tareas/gestionar/actualizar/${id}`;
  const rsp = await postJSON(url, { campo, valor });
  if (rsp && rsp.error) alert("❌ " + rsp.error);
}

export function toggleEstatus(checkbox) {
  const fila = checkbox.closest("tr");
  const id = fila.getAttribute("data-id");
  const estatus = checkbox.checked ? "completada" : "pendiente";
  const nombreNora = document.body.dataset.nombreNora;

  fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/actualizar/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ campo: "estatus", valor: estatus })
  }).then(() => location.reload());
}

export function eliminarTarea(id) {
  const nombreNora = document.body.dataset.nombreNora;
  if (confirm("¿Eliminar esta tarea?")) {
    fetch(`/panel_cliente/${nombreNora}/tareas/eliminar/${id}`, {
      method: "POST"
    }).then(() => location.reload());
  }
}

export function handleAutoCompleteInput(input, campo) {
  const val = input.value.trim();
  if (!val) return;

  const datalistId = input.getAttribute("list");
  const options = document.querySelectorAll(`#${datalistId} option`);
  let id = null;
  options.forEach(opt => {
    if (opt.value === val) id = opt.getAttribute("data-id");
  });

  if (!id) {
    alert("Selecciona una opción válida.");
    return;
  }

  const fila = input.closest("tr");
  const tareaId = fila.getAttribute("data-id");
  const nombreNora = document.body.dataset.nombreNora;

  fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/actualizar/${tareaId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ campo: campo, valor: id })
  }).then(() => location.reload());
}
