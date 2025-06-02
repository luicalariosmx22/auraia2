// ✅ Archivo: static/js/updateCampo.js

// Maneja actualizaciones inline de campos en la tabla de tareas
// Incluye: estatus (checkbox), empresa, asignado, fecha, prioridad, autocompletado y modal editar

// ✅ Actualizar un campo inline
export async function updateCampo(elemento, campo, valorManual = null) {
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
}

// ✅ Checkbox estatus (completada / pendiente)
window.toggleEstatus = function (checkbox) {
  updateCampo(checkbox, "estatus").then(() => location.reload());
};

// ✅ Autocompletar campos con datalist (asignado)
window.handleAutoCompleteInput = function (input, campo) {
  if (campo === "empresa_id") return;  // 🚫 No permitir actualizar empresa

  const val = input.value.trim();
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
  updateCampo(input, campo, id).then(() => location.reload());
};

// ✅ Botón "Ver" para abrir modal de edición
window.cargarTareaEnModal = async function (boton) {
  const tareaId = boton.getAttribute("data-id");
  const nombreNora = boton.getAttribute("data-nora");
  try {
    const res = await fetch(`/panel_cliente/${nombreNora}/tareas/obtener/${tareaId}`);
    const tarea = await res.json();
    if (!tarea || tarea.error) return alert("❌ Error al cargar la tarea");

    document.getElementById("modalTarea").classList.remove("hidden");
    document.getElementById("modalTitulo").textContent = "Ver / Editar tarea";

    document.getElementById("tarea_id").value = tarea.id;
    document.getElementById("titulo").value = tarea.titulo || "";
    document.getElementById("descripcion").value = tarea.descripcion || "";
    document.getElementById("prioridad").value = tarea.prioridad || "media";
    document.getElementById("fecha_limite").value = tarea.fecha_limite || "";

    const asignadoInput = document.getElementById("verAsignado");
    if (asignadoInput) asignadoInput.value = tarea.usuario_empresa_id || "";

    const empresaInput = document.getElementById("verEmpresa");
    if (empresaInput) empresaInput.value = tarea.empresa_id || "";

    const empresaTexto = document.getElementById("verEmpresaTexto");
    if (empresaTexto) empresaTexto.value = tarea.nombre_empresa || "";  // 👈 Asegúrate que venga este campo en el JSON
  } catch (err) {
    console.error("❌ No se pudo cargar la tarea:", err);
  }
};

// ✅ Eliminar tarea desde botón
window.eliminarTarea = function (id) {
  const nombreNora = document.body.dataset.nombreNora;
  if (confirm("¿Eliminar esta tarea?")) {
    fetch(`/panel_cliente/${nombreNora}/tareas/eliminar/${id}`, {
      method: "POST"
    }).then(() => location.reload());
  }
};
