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
  try {
    const chatArea = document.getElementById("chat-area");
    const spinner = document.getElementById("spinner-chat");
    spinner.style.display = "block"; // Mostrar spinner de carga
    chatArea.innerHTML = ""; // Limpiar el área de chat

    const response = await fetch(`/api/chat/${numero}`);
    const data = await response.json();

    spinner.style.display = "none"; // Ocultar spinner de carga

    if (!data.success || !data.mensajes) {
      chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
      return;
    }

    renderizarMensajes(data.mensajes, data.contacto);
    actualizarInfoContacto(data.contacto, data.contacto.resumen || "Sin resumen aún.");
  } catch (error) {
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
  localStorage.setItem("numeroActivo", telefono); // Guardar el número del contacto seleccionado
  cargarChat(telefono); // Cargar el historial del contacto
}

// Enviar un mensaje al contacto seleccionado
async function enviarMensaje(event) {
  event.preventDefault(); // Evitar recargar la página

  const input = document.getElementById("mensaje-input");
  const mensaje = input.value.trim();
  if (!mensaje) return; // No enviar mensajes vacíos

  const telefono = localStorage.getItem("numeroActivo"); // Número del contacto seleccionado
  if (!telefono) {
    mostrarError("No se ha seleccionado un contacto.");
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

      // Agregar el mensaje al área de chat
      const chatArea = document.getElementById("chat-area");
      const div = document.createElement("div");
      div.className = "burbuja usuario";
      div.innerHTML = `
        <div class="remitente">Tú</div>
        <div class="contenido">${mensaje}</div>
        <div class="timestamp">${new Date().toLocaleString()}</div>
      `;
      chatArea.appendChild(div);

      // Limpiar el campo de entrada
      input.value = "";
      chatArea.scrollTop = chatArea.scrollHeight; // Desplazar hacia abajo
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

// Inicializar la página
document.addEventListener("DOMContentLoaded", function () {
  const contactos = document.querySelectorAll(".contacto-item");
  contactos.forEach(contacto => {
    contacto.addEventListener("click", () => seleccionarContacto(contacto.getAttribute("data-numero")));
  });

  const inputEtiqueta = document.getElementById("nueva-etiqueta");
  if (inputEtiqueta) {
    inputEtiqueta.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const telefono = document.getElementById("contacto-telefono").innerText;
        agregarEtiqueta(telefono);
      }
    });
  }
});