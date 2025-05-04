console.log("✅ panel_chat.js cargado correctamente");

let contactoActual = null;
let historial = [];
let offset = 0;
let numeroActual = null;
let contactoSeleccionado = null;

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
    div.className = mensaje.emisor === "nora" ? "message sent" : "message received"; // Updated class names

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

// Reordenar contactos
function reordenarContactos() {
  console.log("🔍 Iniciando reordenamiento de contactos...");
  const lista = document.getElementById("lista-contactos");
  const items = Array.from(lista.querySelectorAll(".contacto-item"));

  console.log("🔍 Ordenando contactos por fecha del último mensaje...");
  items.sort((a, b) => {
    const fechaA = new Date(a.querySelector(".fecha-ultimo-contacto").innerText || "1900-01-01");
    const fechaB = new Date(b.querySelector(".fecha-ultimo-contacto").innerText || "1900-01-01");
    return fechaB - fechaA; // Ordenar de más reciente a más antiguo
  });

  console.log("🔍 Reinsertando contactos en el DOM...");
  items.forEach(item => lista.appendChild(item)); // Reinsertar en orden
  console.log("✅ Contactos reordenados.");
}

// Filtrar contactos por nombre
function filtrarContactosPorNombre(nombre) {
  console.log(`🔍 Filtrando contactos por nombre: ${nombre}`);
  const listaContactos = document.getElementById("lista-contactos");
  const items = listaContactos.querySelectorAll(".contacto-item");

  items.forEach(item => {
    const nombreContacto = item.querySelector(".contacto-nombre").innerText.toLowerCase();
    const visible = nombreContacto.includes(nombre.toLowerCase());
    console.log(`🔍 Contacto: ${nombreContacto}, Visible: ${visible}`);
    item.style.display = visible ? "" : "none";
  });
}

// Filtrar contactos por etiqueta
function filtrarContactosPorEtiqueta(etiqueta) {
  console.log(`🔍 Filtrando contactos por etiqueta: ${etiqueta}`);
  const listaContactos = document.getElementById("lista-contactos");
  const items = listaContactos.querySelectorAll(".contacto-item");

  items.forEach(item => {
    const etiquetas = Array.from(item.querySelectorAll(".etiqueta")).map(e => e.innerText.toLowerCase());
    const visible = etiqueta === "" || etiquetas.includes(etiqueta.toLowerCase());
    console.log(`🔍 Contacto etiquetas: ${etiquetas}, Visible: ${visible}`);
    item.style.display = visible ? "" : "none";
  });
}

// Enviar un mensaje al contacto seleccionado
async function enviarMensaje(event) {
  event.preventDefault();
  console.log("🔍 Iniciando envío de mensaje...");

  const input = document.getElementById("mensaje-input");
  const mensaje = input.value.trim();
  console.log(`🔍 Mensaje a enviar: ${mensaje}`);
  if (!mensaje) {
    console.warn("⚠️ Mensaje vacío. Cancelando envío.");
    return;
  }

  const telefono = localStorage.getItem("numeroActivo");
  console.log(`🔍 Enviando mensaje al número: ${telefono}`);
  if (!telefono || telefono === "null" || telefono === "undefined") {
    mostrarError("No se ha seleccionado un contacto válido.");
    return;
  }

  try {
    console.log("🔍 Enviando solicitud al servidor...");
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
    console.log("🔍 Respuesta del servidor:", data);
    if (data.success) {
      console.log("✅ Mensaje enviado correctamente.");
      input.value = "";

      // 🔥 Actualizar visualmente el contacto
      const contactoItem = document.querySelector(`.contacto-item[data-numero="${telefono}"]`);
      if (contactoItem) {
        const ultimoMensaje = contactoItem.querySelector(".ultimo-mensaje");
        const fechaContacto = contactoItem.querySelector(".fecha-ultimo-contacto");

        if (ultimoMensaje) {
          console.log("🔍 Actualizando último mensaje en la lista de contactos...");
          ultimoMensaje.textContent = mensaje;
        }
        if (fechaContacto) {
          console.log("🔍 Actualizando fecha del último mensaje...");
          const ahora = new Date();
          fechaContacto.textContent = ahora.toISOString().slice(0, 19).replace("T", " ");
        }
      }

      // 🔥 REORDENAR
      console.log("🔍 Reordenando contactos después del envío...");
      reordenarContactos();
    } else {
      console.error("❌ Error al enviar el mensaje.");
      mostrarError("Error al enviar el mensaje.");
    }
  } catch (err) {
    console.error("❌ Error al enviar el mensaje:", err);
    manejarError(err, "Error al enviar el mensaje.");
  }
}

// Función para seleccionar un contacto
function seleccionarContacto(elemento) {
  // Quitar la clase 'selected' de todos los contactos
  const contactos = document.querySelectorAll('.sidebar .contacto');
  contactos.forEach(contacto => contacto.classList.remove('selected'));

  // Agregar la clase 'selected' al contacto actual
  elemento.classList.add('selected');

  // Actualizar el encabezado con el nombre del contacto
  const nombre = elemento.querySelector('.nombre').innerText;
  document.getElementById('nombre-contacto').innerText = nombre;
  document.getElementById('estado-contacto').innerText = "Conectado"; // Puedes ajustar esto dinámicamente

  // Guardar el contacto seleccionado
  contactoSeleccionado = nombre;

  // Cargar mensajes del contacto
  cargarMensajes(nombre);
}

// Abrir chat para un contacto
function abrirChat(telefono) {
  console.log(`📥 Abriendo chat para teléfono: ${telefono}`);
  
  // Quitar la clase 'selected' de todos los contactos
  document.querySelectorAll('.contacto-item').forEach(item => {
    item.classList.remove('selected');
  });
  console.log("✅ Clase 'selected' removida de todos los contactos.");

  // Agregar la clase 'selected' al contacto actual
  const contactoActual = document.querySelector(`.contacto-item[data-numero="${telefono}"]`);
  if (contactoActual) {
    contactoActual.classList.add('selected');
    console.log(`✅ Clase 'selected' añadida al contacto: ${telefono}`);
  } else {
    console.log(`⚠️ No se encontró el contacto con teléfono: ${telefono}`);
  }

  // Cargar mensajes del contacto
  fetch(`/api/chat/${telefono}`)
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const contenedor = document.getElementById("chat-mensajes");
        const nombre = document.getElementById("nombre-contacto");
        nombre.innerText = data.contacto.nombre || data.contacto.telefono;

        contenedor.innerHTML = "";
        data.mensajes.forEach(m => {
          const burbuja = document.createElement("div");
          burbuja.className = m.emisor === "nora" ? "mensaje nora" : "mensaje cliente";
          burbuja.innerHTML = `
            <div class="remitente">${m.emisor === "nora" ? "Nora" : data.contacto.nombre}</div>
            <div class="contenido">${m.mensaje}</div>
            <div class="hora">${m.hora || ""}</div>
          `;
          contenedor.appendChild(burbuja);
        });

        scrollAlFinal();
      } else {
        console.error("❌ Error al cargar el historial.");
      }
    })
    .catch(err => console.error("❌ Error en la solicitud:", err));
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

    const telefono = data.telefono;

    // Actualizar último mensaje en la lista de contactos
    const contactoItem = document.querySelector(`.contacto-item[data-numero="${telefono}"]`);
    if (contactoItem) {
        const ultimoMensaje = contactoItem.querySelector(".ultimo-mensaje");
        const fechaContacto = contactoItem.querySelector(".fecha-ultimo-contacto");

        if (ultimoMensaje) {
            ultimoMensaje.textContent = data.mensaje; // Actualiza el mensaje
        }
        if (fechaContacto) {
          const ahora = new Date();
          fechaContacto.textContent = ahora.toISOString().slice(0, 19).replace("T", " ");
        }
    }

    // Insertar el mensaje en el chat si el chat abierto corresponde
    if (telefono === localStorage.getItem("numeroActivo")) {
        const chat = document.getElementById("chat-area");
        const nuevoMensaje = document.createElement("div");
        nuevoMensaje.classList.add("burbuja", data.remitente === "bot" ? "nora" : "usuario");

        nuevoMensaje.innerHTML = `
            <div class="remitente">${data.remitente === "bot" ? "Nora" : "Tú"}</div>
            <div class="contenido">${data.mensaje}</div>
            <div class="timestamp">${new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</div>
        `;
        chat.appendChild(nuevoMensaje);
        chat.scrollTop = chat.scrollHeight;
    }

    // 🔥 REORDENAR toda la lista
    reordenarContactos();
});

// Add event listeners for sending messages
document.getElementById("enviar-btn").addEventListener("click", enviarMensaje);
document.getElementById("mensaje-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") enviarMensaje();
});

document.querySelectorAll('.sidebar .contacto').forEach(contacto => {
  contacto.addEventListener('click', () => {
    seleccionarContacto(contacto);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const contactList = document.getElementById("contactList");
  const chatHeader = document.getElementById("chatHeader");
  const chatMessages = document.getElementById("chatMessages");
  const sendButton = document.getElementById("sendButton");
  const messageInput = document.getElementById("messageInput");

  // Simulación de carga de contactos
  console.log("Cargando contactos...");
  fetch("/api/chat/contacts")
    .then((response) => response.json())
    .then((contacts) => {
      console.log("Contactos cargados:", contacts);
      contactList.innerHTML = ""; // Limpiar mensaje de carga
      contacts.forEach((contact) => {
        const contactItem = document.createElement("div");
        contactItem.classList.add("contact-item");
        contactItem.innerHTML = `
          <img src="${contact.image || 'default-profile.png'}" alt="Avatar" class="avatar" />
          <div class="contact-info">
            <p class="contact-name">${contact.name}</p>
            <p class="last-message">${contact.lastMessage}</p>
          </div>
        `;
        contactItem.addEventListener("click", () => {
          loadChat(contact);
        });
        contactList.appendChild(contactItem);
      });
    })
    .catch((error) => {
      console.error("Error al cargar contactos:", error);
      contactList.innerHTML = "<p>Error al cargar contactos.</p>";
    });

  // Función para cargar el chat de un contacto
  function loadChat(contact) {
    console.log("Cargando chat para:", contact.name);
    chatHeader.innerHTML = `
      <img src="${contact.image || 'default-profile.png'}" alt="Avatar" class="avatar" />
      <div class="chat-info">
        <p class="contact-name">${contact.name}</p>
        <p class="status">Conectado</p>
      </div>
    `;
    fetch(`/api/chat/${contact.phone}`)
      .then((response) => response.json())
      .then((data) => {
        console.log("Mensajes cargados:", data.messages);
        chatMessages.innerHTML = ""; // Limpiar mensaje de "No hay mensajes"
        data.messages.forEach((message) => {
          const messageElement = document.createElement("div");
          messageElement.classList.add(
            "message",
            message.sender === "me" ? "own-message" : "contact-message"
          );
          messageElement.innerHTML = `
            <p>${message.text}</p>
            <span class="timestamp">${message.timestamp}</span>
          `;
          chatMessages.appendChild(messageElement);
        });
      })
      .catch((error) => {
        console.error("Error al cargar mensajes:", error);
        chatMessages.innerHTML = "<p>Error al cargar mensajes.</p>";
      });
  }

  // Enviar mensaje
  sendButton.addEventListener("click", () => {
    const message = messageInput.value.trim();
    if (message) {
      console.log("Enviando mensaje:", message);
      fetch("/api/enviar-mensaje", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Mensaje enviado:", data);
          // Agregar mensaje al chat
          const messageElement = document.createElement("div");
          messageElement.classList.add("message", "own-message");
          messageElement.innerHTML = `
            <p>${message}</p>
            <span class="timestamp">Ahora</span>
          `;
          chatMessages.appendChild(messageElement);
          messageInput.value = ""; // Limpiar input
          chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll al final
        })
        .catch((error) => {
          console.error("Error al enviar mensaje:", error);
        });
    }
  });
});