// Solo flujo moderno para el modal de creación de tarea
const formNueva = document.getElementById("formTareaNueva");
let enviando = false;
if (formNueva) {
  console.debug('[DEBUG] Script tareas_modal_nueva.js cargado. formTareaNueva existe:', !!formNueva);
  formNueva.addEventListener("submit", async function (e) {
    e.preventDefault();
    const form = e.target;
    console.debug('[DEBUG] Submit capturado en formTareaNueva');

    if (enviando) {
      console.warn("⛔ Ignorado doble envío.");
      return;
    }

    enviando = true;
    const boton = form.querySelector("button[type='submit']");
    if (boton) {
      console.debug('[DEBUG] Botón submit encontrado:', boton);
      boton.disabled = true;
      boton.classList.add("bg-yellow-400", "cursor-wait");
      boton.textContent = "Enviando...";
    } else {
      console.warn('[DEBUG] No se encontró el botón submit dentro del form');
    }

    // Validación de usuario asignado
    let usuario_empresa_id = null;
    const selectUser = document.getElementById("usuario_empresa_id_modal");
    const hiddenUser = document.getElementById("usuario_empresa_id_hidden");
    console.debug('[DEBUG] selectUser:', selectUser, 'valor:', selectUser?.value, 'disabled:', selectUser?.disabled);
    console.debug('[DEBUG] hiddenUser:', hiddenUser, 'valor:', hiddenUser?.value);
    if (selectUser && !selectUser.disabled && selectUser.value && selectUser.value !== "None" && selectUser.value !== "none") {
      usuario_empresa_id = selectUser.value;
    } else if (hiddenUser && hiddenUser.value && hiddenUser.value !== "None" && hiddenUser.value !== "none") {
      usuario_empresa_id = hiddenUser.value;
    }
    console.debug('[DEBUG] usuario_empresa_id detectado:', usuario_empresa_id);

    if (!usuario_empresa_id || usuario_empresa_id === "" || usuario_empresa_id === "None" || usuario_empresa_id === "none") {
      alert("❌ Debes seleccionar un usuario válido");
      enviando = false;
      if (boton) {
        boton.disabled = false;
        boton.classList.remove("bg-yellow-400", "cursor-wait");
        boton.textContent = "Guardar";
      }
      console.warn('[DEBUG] Validación usuario_empresa_id falló');
      return;
    }

    const userId = window?.user?.id || null;
    const payload = {
      titulo: document.getElementById("titulo")?.value,
      descripcion: document.getElementById("descripcion")?.value,
      prioridad: document.getElementById("prioridad")?.value,
      estatus: document.getElementById("estatus")?.value,
      fecha_limite: document.getElementById("fecha_limite")?.value || null,
      usuario_empresa_id: usuario_empresa_id,
      empresa_id: document.getElementById("empresa_id_modal")?.value,
      creado_por: document.querySelector('[name="creado_por"]')?.value || userId || null,
      is_recurrente: document.getElementById("recurrente_checkbox")?.checked ? "true" : "false",
      dtstart: document.getElementById("dtstart")?.value || null,
      rrule: document.getElementById("rrule")?.value || null,
      until: document.getElementById("until")?.value || null,
      count: document.getElementById("count")?.value || null
    };
    // Si el formulario incluye tarea_padre_id (creación de subtarea), añádelo al payload
    const tareaPadreInput = document.getElementById("tarea_padre_id");
    if (tareaPadreInput && tareaPadreInput.value) {
      payload.tarea_padre_id = tareaPadreInput.value;
      // Eliminar nombre_nora si existe en el payload
      if (payload.nombre_nora) delete payload.nombre_nora;
    } else {
      // Solo para tareas normales, si necesitas nombre_nora, puedes agregarlo aquí
      // payload.nombre_nora = document.querySelector('[name="nombre_nora"]')?.value;
    }

    console.debug("🟡 Payload enviado:", payload);
    console.debug("[DEBUG] creado_por:", payload.creado_por);
    console.debug("[DEBUG] usuario_empresa_id:", payload.usuario_empresa_id);

    try {
      let nombreNora = document.body.dataset.nora;
      let url = `/panel_cliente/${nombreNora}/tareas/gestionar`;
      console.debug('[DEBUG] URL de fetch:', url);
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      console.debug("📩 Estado HTTP:", res.status); // 👈 AÑADE ESTO

      const resultado = await res.json().catch(err => {
        console.error("❌ Error parsing JSON:", err);
        return { error: "Respuesta no válida del backend" };
      });

      console.debug("🟢 Respuesta backend:", resultado);

      if (resultado.ok || resultado.id) {
        console.debug('[DEBUG] Tarea creada correctamente, cerrando modal');
        cerrarModalTarea();
        if (window.insertarTareaEnTabla) {
          const tarea = resultado.tarea || resultado;
          window.insertarTareaEnTabla(tarea);
        }
        if (window.mostrarNotificacion) {
          window.mostrarNotificacion("✅ Tarea guardada exitosamente");
        } else {
          alert("✅ Tarea guardada exitosamente");
        }
        form.reset();
      } else {
        console.warn('[DEBUG] Error backend:', resultado.error);
        alert("❌ Error: " + (resultado.error || "No se pudo crear la tarea"));
      }
    } catch (err) {
      console.error("❌ Error de red o backend:", err);
      alert("❌ Error inesperado al guardar la tarea");
    } finally {
      enviando = false;
      if (boton) {
        boton.disabled = false;
        boton.classList.remove("bg-yellow-400", "cursor-wait");
        boton.textContent = "Guardar";
        console.debug('[DEBUG] Botón submit reactivado');
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", function() {
  var btnCancelar = document.getElementById("btnCancelarTarea");
  if(btnCancelar) {
    btnCancelar.onclick = function() {
      document.getElementById("modalTarea").classList.add("hidden");
    }
  }
});

// --- Refuerzo: poblar datalist de tareas activas para subtarea ---
async function poblarDatalistTareasActivas() {
  const datalist = document.getElementById("tareas_activas_datalist");
  if (!datalist) return;
  // Limpiar datalist
  datalist.innerHTML = "";
  let nombreNora = document.body.dataset.nora;
  let url = `/panel_cliente/${nombreNora}/tareas/activas_para_subtarea`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("No se pudieron obtener tareas activas");
    const data = await res.json();
    if (Array.isArray(data.tareas)) {
      data.tareas.forEach(tarea => {
        const option = document.createElement("option");
        option.value = tarea.id;
        option.text = tarea.titulo;
        datalist.appendChild(option);
      });
    }
  } catch (err) {
    console.error("❌ Error al poblar datalist de tareas activas:", err);
  }
}

// Llama a poblarDatalistTareasActivas cada vez que se abre el modal de nueva subtarea
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
    poblarDatalistTareasActivas(); // <-- poblar datalist cada vez
  }
};

window.cerrarModalTarea = function () {
  document.getElementById("modalNuevaTarea").classList.add("hidden");
};

// 👉 Toggle y validación de campos de recurrencia en el modal “Nueva tarea”
document.addEventListener("DOMContentLoaded", () => {
  const chk = document.getElementById("recurrente_checkbox");
  const box = document.getElementById("recurrente_fields");
  const dt  = document.getElementById("dtstart");
  const rr  = document.getElementById("rrule");

  if (!chk || !box) return;

  const toggle = () => {
    const on = chk.checked;
    box.classList.toggle("hidden", !on);
    if (dt) dt.required = on;
    if (rr) rr.required = on;
    if (!on) {
      if (dt) dt.value = "";
      if (rr) rr.value = "FREQ=DAILY";
      const until = document.getElementById("until");
      const count = document.getElementById("count");
      if (until) until.value = "";
      if (count) count.value = "";
    }
  };

  chk.addEventListener("change", toggle);
  toggle(); // estado inicial
});