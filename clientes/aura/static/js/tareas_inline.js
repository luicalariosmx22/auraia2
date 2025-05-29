// Funciones utilitarias para peticiones fetch usadas en la vista de tareas
// ───────────────────────────────────────────────────────────────────────────
// util POST JSON + envío del formulario del modal "Nueva tarea"
// ───────────────────────────────────────────────────────────────────────────

async function postJSON(url, payload = {}) {
  // Enviar como FormData para que el backend lo reciba como request.form
  const formData = new FormData();
  for (const key in payload) {
    if (payload[key] !== undefined && payload[key] !== null) {
      formData.append(key, payload[key]);
    }
  }
  const res = await fetch(url, {
    method: "POST",
    body: formData
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
      titulo:               get("titulo").value.trim(),
      descripcion:          get("descripcion").value.trim(),
      fecha_limite:         get("fecha_limite").value || null,
      prioridad:            get("prioridad").value.toLowerCase(),
      usuario_empresa_id:   get("usuario_empresa_id").value
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

function editarTarea(id) {
  const fila = [...document.querySelectorAll("tr")].find(row => row.innerHTML.includes(id));
  if (!fila) return;

  document.getElementById("modalTarea").classList.remove("hidden");
  document.getElementById("tarea_id").value = id;
  document.getElementById("modalTitulo").textContent = "Ver tarea";

  document.getElementById("titulo").value = fila.children[1].innerText.trim();

  const prioridadTxt = fila.children[2].innerText.trim().replace(/^[^\w]+/, "");
  document.getElementById("prioridad").value = prioridadTxt.toLowerCase();

  document.getElementById("fecha_limite").value = fila.children[3].innerText.trim();

  const empresaSelect = document.getElementById("empresa_id");
  const empresaTexto = fila.children[6].innerText.trim();
  [...empresaSelect.options].forEach(option => {
    option.selected = option.text.trim() === empresaTexto;
  });

  // 🚀 Cargar descripción desde Supabase
  const nombreNora = document.body.dataset.nombreNora;
  fetch(`/panel_cliente/${nombreNora}/tareas/obtener/${id}`)
    .then(res => res.json())
    .then(data => {
      if (data.descripcion) {
        document.getElementById("descripcion").value = data.descripcion;
      }
    })
    .catch(err => console.error("Error al cargar la descripción:", err));
}
