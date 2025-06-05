// Elimina legacy y deja solo el flujo para el modal de creación actual

// Nuevo flujo para el modal de creación de tarea
const formNueva = document.getElementById("formTareaNueva");
let enviando = false;
if (formNueva) {
  formNueva.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (enviando) return;
    enviando = true;

    const form = e.target;
    // Armar payload manualmente para asegurar campos de recurrencia
    // ⚠️ Tomar usuario_empresa_id del input hidden si el select está deshabilitado
    let usuario_empresa_id = null;
    const selectUser = document.getElementById("usuario_empresa_id_modal");
    const hiddenUser = document.getElementById("usuario_empresa_id_hidden");
    // Si el select existe y NO está deshabilitado, usa su valor
    if (selectUser && !selectUser.disabled && selectUser.value && selectUser.value !== "None" && selectUser.value !== "none") {
      usuario_empresa_id = selectUser.value;
    } else if (hiddenUser && hiddenUser.value && hiddenUser.value !== "None" && hiddenUser.value !== "none") {
      usuario_empresa_id = hiddenUser.value;
    }
    // Validación extra: si sigue siendo null, mostrar mensaje claro
    if (!usuario_empresa_id || usuario_empresa_id === "" || usuario_empresa_id === "None" || usuario_empresa_id === "none") {
      // Si hay un objeto global user, mostrar info extra
      let userId = window.user && window.user.id ? window.user.id : null;
      let msg = "Debes seleccionar un usuario asignado válido. Valor actual: " + usuario_empresa_id;
      if (!userId) {
        msg += "\n[ADVERTENCIA] El usuario actual no está definido en el contexto JS (window.user.id es null o vacío). Contacta a soporte.";
      }
      alert(msg);
      enviando = false;
      return;
    }
    const payload = {
      titulo: document.getElementById("titulo")?.value,
      descripcion: document.getElementById("descripcion")?.value,
      prioridad: document.getElementById("prioridad")?.value,
      estatus: document.getElementById("estatus")?.value,
      fecha_limite: document.getElementById("fecha_limite")?.value,
      usuario_empresa_id: usuario_empresa_id,
      empresa_id: document.getElementById("empresa_id_modal")?.value,
      cliente_id: document.querySelector('[name="cliente_id"]')?.value,
      creado_por: document.querySelector('[name="creado_por"]')?.value,
      nombre_nora: document.querySelector('[name="nombre_nora"]')?.value,
      iniciales_usuario: document.querySelector('[name="iniciales_usuario"]')?.value,
      is_recurrente: document.getElementById("recurrente_checkbox")?.checked ? "true" : "false",
      dtstart: document.getElementById("dtstart")?.value,
      rrule: document.getElementById("rrule")?.value,
      until: document.getElementById("until")?.value,
      count: document.getElementById("count")?.value
    };
    const nombreNora = payload.nombre_nora;

    try {
      const res = await fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/crear`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const resultado = await res.json();
      if (resultado.ok || resultado.id) {
        cerrarModalTarea();
        if (window.insertarTareaEnTabla) {
          // El backend regresa la tarea en resultado.tarea o resultado
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
        // Mostrar mensaje de error del backend si existe
        let msg = resultado.error || "No se pudo crear la tarea";
        alert("❌ Error: " + msg);
        // Opcional: mostrar el error en el modal en vez de alert
        // document.getElementById("errorNuevaTarea").textContent = msg;
      }
    } catch (err) {
      console.error(err);
      alert("❌ Error inesperado al guardar la tarea");
    } finally {
      enviando = false;
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