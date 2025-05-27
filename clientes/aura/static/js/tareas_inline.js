// Funciones utilitarias para peticiones fetch usadas en la vista de tareas
// ───────────────────────────────────────────────────────────────────────────
// util POST JSON + envío del formulario del modal "Nueva tarea"
// ───────────────────────────────────────────────────────────────────────────
async function postJSON(url, payload = {}) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) {
    alert("❌ " + (data.error || res.statusText));
    throw new Error(data.error || res.statusText);
  }
  return data;
}

function initModalSubmit() {
  const form = document.getElementById("formTarea");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      titulo: document.getElementById("titulo").value.trim(),
      descripcion: document.getElementById("descripcion").value.trim(),
      fecha_limite: document.getElementById("fecha_limite").value || null,
      // enviamos en minúsculas
      prioridad: document.getElementById("prioridad").value.toLowerCase(),
      empresa_id: document.getElementById("empresa_id").value || null,
      usuario_empresa_id: document.getElementById("usuario_empresa_id").value,
      nombre_nora: document.getElementById("nombre_nora").value,
      creado_por: document.getElementById("usuario_sesion").value
    };

    const nora = payload.nombre_nora;
    const url = `/panel_cliente/${nora}/tareas/gestionar/crear`;

    try {
      await postJSON(url, payload);
      location.reload();
    } catch (_) { /* error ya alertado */ }
  });
}

initModalSubmit();
