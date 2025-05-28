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
    // ─── seleccionar elementos por ID usando get() ─────────────────────
    const get = id => document.getElementById(id);
    const payload = {
      titulo:             get("titulo").value.trim(),
      descripcion:        get("descripcion").value.trim(),
      fecha_limite:       get("fecha_limite").value || null,
      prioridad:          get("prioridad").value.toLowerCase(),
      usuario_empresa_id: get("usuario_empresa_id").value
    };

    const emp = get("empresa_id").value;
    if (emp) payload.empresa_id = emp;

    const nombre_nora = get("nombre_nora").value;
    const url = `/panel_cliente/${nombre_nora}/tareas/gestionar/crear`;

    try {
      await postJSON(url, payload);
      location.reload();
    } catch (_) { /* error ya alertado */ }
  });
}

initModalSubmit();

/* -------------------------------------------------------------
   Función auxiliar usada en gestores inline (títulos, estatus…)
------------------------------------------------------------- */
export async function updateField(id, campo, valor, nombreNora) {
  const url = `/panel_cliente/${nombreNora}/tareas/gestionar/actualizar/${id}`;
  const rsp = await postJSON(url, { campo, valor });
  if (rsp && rsp.error) alert("❌ " + rsp.error);
}
