console.log("✅ panel_chat.js cargado correctamente");

let contactoActual = null;
let historial = [];
let offset = 0;
let numeroActual = null;

// Mostrar errores al usuario
function mostrarError(mensaje) {
  alert(`❌ ${mensaje}`);
}

// Manejar errores en la consola y mostrar al usuario
function manejarError(err, mensaje) {
  console.error(err);
  mostrarError(mensaje);
}

// Cargar el historial de chat de un contacto
async function cargarChat(numero) {
  console.log(`🔍 Iniciando carga del historial para el número: ${numero}`);
  try {
    const chatArea = document.getElementById("chat-area");
    const spinner = document.getElementById("spinner-chat");
    spinner.style.display = "block"; // Mostrar spinner de carga
    chatArea.innerHTML = ""; // Limpiar el área de chat

    console.log("🔍 Enviando solicitud al backend...");
    const response = await fetch(`/api/chat/${numero}`);
    console.log(`🔍 Respuesta recibida del servidor: ${response.status}`);

    if (!response.ok) {
      console.error(`❌ Error en la respuesta del servidor: ${response.statusText}`);
      manejarError(null, "Error al cargar el historial de chat.");
      return;
    }

    const data = await response.json();
    console.log("🔍 Datos recibidos del servidor:", data);

    spinner.style.display = "none"; // Ocultar spinner de carga

    if (!data.success || !data.mensajes) {
      console.error("❌ Error: No se encontraron mensajes o la respuesta no fue exitosa.");
      chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
      return;
    }

    console.log("✅ Historial cargado correctamente. Renderizando mensajes...");
    renderizarMensajes(data.mensajes, data.contacto);
    actualizarInfoContacto(data.contacto, data.contacto.resumen || "Sin resumen aún.");

    // 🔥 REORDENAR AL FINAL DESPUÉS DE CARGAR
    reordenarContactos();

  } catch (error) {
    console.error("❌ Error al cargar el historial de chat:", error);
    manejarError(error, "Error al cargar el historial de chat.");
    const chatArea = document.getElementById("chat-area");
    chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
  }
}

// Renderizar los mensajes en el área de chat
function renderizarMensajes(mensajes, contacto) {
  const chatArea = document.getElementById("chat-area");
  chatArea.innerHTML = ""; // Limpiar el área de chat

  mensajes.forEach(mensaje => {
    const div = document.createElement("div");
    div.className = `burbuja ${mensaje.emisor === "nora" ? "nora" : "contacto"}`;

    // Mostrar el remitente
    const remitente = document.createElement("div");
    remitente.className = "remitente";
    remitente.innerText = mensaje.remitente;

    // Mostrar el contenido del mensaje
    const contenido = document.createElement("div");
    contenido.className = "contenido";
    contenido.innerText = mensaje.mensaje;

    // Mostrar el timestamp
    const timestamp = document.createElement("div");
    timestamp.className = "timestamp";
    timestamp.innerText = mensaje.fecha || "Sin fecha";

    div.appendChild(remitente);
    div.appendChild(contenido);
    div.appendChild(timestamp);

    chatArea.appendChild(div);
  });

  chatArea.scrollTop = chatArea.scrollHeight; // Desplazar hacia abajo
}

// Actualizar la información del contacto seleccionado
function actualizarInfoContacto(contacto, resumen) {
  document.getElementById("contacto-nombre").innerText = contacto.nombre || "Sin nombre";
  document.getElementById("contacto-telefono").innerText = contacto.telefono || "";
  document.getElementById("resumen-ia").innerText = resumen || "Sin resumen aún.";
  renderizarEtiquetas(contacto.etiquetas || [], contacto.telefono);
}

// Renderizar las etiquetas del contacto
function renderizarEtiquetas(etiquetas, telefono) {
  const contenedor = document.getElementById("contacto-tags");
  contenedor.innerHTML = "";
  etiquetas.forEach(etiqueta => {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.innerHTML = `${etiqueta} <span class="x" onclick="eliminarEtiqueta(event, '${telefono}', '${etiqueta}')">✖</span>`;
    contenedor.appendChild(tag);
  });
}

// Eliminar una etiqueta del contacto
async function eliminarEtiqueta(event, telefono, etiqueta) {
  event.stopPropagation(); // Evitar seleccionar contacto por error

  try {
    const response = await fetch(`/api/etiqueta/${telefono}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ etiqueta })
    });

    if (response.ok) {
      seleccionarContacto(telefono); // Recargar datos del contacto
    }
  } catch (error) {
    manejarError(error, "Error al eliminar la etiqueta.");
  }
}

// Agregar una etiqueta al contacto
async function agregarEtiqueta(telefono) {
  const input = document.getElementById("nueva-etiqueta");
  const etiqueta = input.value.trim().toLowerCase();
  if (!etiqueta) return;

  try {
    const response = await fetch(`/api/etiqueta/${telefono}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ etiqueta })
    });

    if (response.ok) {
      seleccionarContacto(telefono); // Recargar para mostrar nueva etiqueta
      input.value = "";
    }
  } catch (error) {
    manejarError(error, "Error al agregar la etiqueta.");
  }
}

// Seleccionar un contacto y cargar su historial
function seleccionarContacto(telefono) {
  console.log(`🔍 Seleccionando contacto con el número: ${telefono}`);
  
  // Guardar el número del contacto seleccionado en localStorage
  localStorage.setItem("numeroActivo", telefono);
  console.log(`✅ Número guardado en localStorage: ${localStorage.getItem("numeroActivo")}`);
  
  // Llamar a la función cargarChat para cargar el historial del contacto
  cargarChat(telefono);
}

// Enviar un mensaje al contacto seleccionado
async function enviarMensaje(event) {
  event.preventDefault(); // Evitar recargar la página

  const input = document.getElementById("mensaje-input");
  const mensaje = input.value.trim();
  if (!mensaje) return; // No enviar mensajes vacíos

  const telefono = localStorage.getItem("numeroActivo");
  if (!telefono || telefono === "null" || telefono === "undefined") {
    mostrarError("No se ha seleccionado un contacto válido.");
    return;
  }

  try {
    const response = await fetch("/api/enviar-mensaje", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        numero: telefono,
        mensaje: mensaje
      })
    });

    const data = await response.json();
    if (data.success) {
      console.log("✅ Mensaje enviado:", mensaje);
      input.value = ""; // Limpiar input
      // Esperamos a que el mensaje se renderice por Socket.IO
    } else {
      mostrarError("Error al enviar el mensaje.");
    }
  } catch (err) {
    manejarError(err, "Error al enviar el mensaje.");
  }
}

// Filtrar contactos por nombre
function filtrarContactosPorNombre(nombre) {
  const listaContactos = document.getElementById("lista-contactos");
  const items = listaContactos.querySelectorAll(".contacto-item");
  items.forEach(item => {
    const nombreContacto = item.querySelector(".contacto-nombre").innerText.toLowerCase();
    item.style.display = nombreContacto.includes(nombre.toLowerCase()) ? "" : "none";
  });
}

// Filtrar contactos por etiqueta
function filtrarContactosPorEtiqueta(etiqueta) {
  const listaContactos = document.getElementById("lista-contactos");
  const items = listaContactos.querySelectorAll(".contacto-item");
  items.forEach(item => {
    const etiquetas = Array.from(item.querySelectorAll(".etiqueta")).map(e => e.innerText.toLowerCase());
    item.style.display = etiqueta === "" || etiquetas.includes(etiqueta.toLowerCase()) ? "" : "none";
  });
}

// Reordenar contactos
function reordenarContactos() {
  const lista = document.getElementById("lista-contactos");
  const items = Array.from(lista.querySelectorAll(".contacto-item"));

  items.sort((a, b) => {
    const fechaA = new Date(a.querySelector(".fecha-ultimo-contacto").innerText || "1900-01-01");
    const fechaB = new Date(b.querySelector(".fecha-ultimo-contacto").innerText || "1900-01-01");
    return fechaB - fechaA; // Ordenar de más reciente a más antiguo
  });

  items.forEach(item => lista.appendChild(item)); // Reinsertar en orden
}

// Inicializar la página
document.addEventListener("DOMContentLoaded", function () {
  const contactos = document.querySelectorAll(".contacto-item");

  // Añadir evento click a cada contacto
  contactos.forEach(contacto => {
    contacto.addEventListener("click", () => {
      const telefono = contacto.getAttribute("data-numero");
      console.log(`🔍 Contacto seleccionado: ${telefono}`);
      seleccionarContacto(telefono);
    });
  });

  // Verifica si hay un número guardado en localStorage
  const numeroGuardado = localStorage.getItem("numeroActivo");
  if (numeroGuardado && numeroGuardado !== "null") {
    console.log("📦 Cargando historial guardado:", numeroGuardado);
    cargarChat(numeroGuardado);
  } else if (contactos.length > 0) {
    // Si no hay número guardado, cargar el primer contacto de la lista
    const primerTelefono = contactos[0].getAttribute("data-numero");
    console.log("📲 No había número guardado. Cargando primer contacto:", primerTelefono);
    seleccionarContacto(primerTelefono);
  } else {
    // Si no hay contactos en la lista
    console.warn("⚠️ No hay contactos en la lista.");
  }
});

// ✅ Inicializar conexión con Socket.IO
const socket = io();

// ✅ Escuchar el evento "nuevo_mensaje" desde el servidor
socket.on("nuevo_mensaje", (data) => {
    console.log("📩 Nuevo mensaje recibido:", data);

    const chat = document.getElementById("chat-area");
    const nuevoMensaje = document.createElement("div");
    nuevoMensaje.classList.add("burbuja", data.remitente === "bot" ? "nora" : "usuario");

    nuevoMensaje.innerHTML = `
        <div class="remitente">${data.remitente === "bot" ? "Nora" : "Tú"}</div>
        <div class="contenido">${data.mensaje}</div>
        <div class="timestamp">${new Date().toLocaleTimeString()}</div>
    `;

    chat.appendChild(nuevoMensaje);
    chat.scrollTop = chat.scrollHeight;

    // 🔥 Y también reordenamos contactos cada que llegue un nuevo mensaje
    reordenarContactos();
});