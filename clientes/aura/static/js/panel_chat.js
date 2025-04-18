console.log("✅ panel_chat.js cargado correctamente");

let contactoActual = null;
let historial = [];
let offset = 0;
let numeroActual = null;

function mostrarError(mensaje) {
    alert(`❌ ${mensaje}`);
}

function manejarError(err, mensaje) {
    console.error(err);
    mostrarError(mensaje);
}

// Nueva implementación de cargarChat con async/await
async function cargarChat(numero) {
  try {
    const response = await fetch(`/api/chat/${numero}`);
    const data = await response.json();

    const chatArea = document.getElementById("chat-area");
    chatArea.innerHTML = ""; // Limpiar el área de chat

    if (!data.success || !data.mensajes) {
      chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
      return;
    }

    data.mensajes.forEach(mensaje => {
      const div = document.createElement("div");
      div.className = `burbuja ${mensaje.emisor === "nora" ? "nora" : "contacto"}`;

      const remitente = document.createElement("div");
      remitente.className = "remitente";
      remitente.innerText = mensaje.remitente;

      const contenido = document.createElement("div");
      contenido.className = "contenido";
      contenido.innerText = mensaje.mensaje;

      const timestamp = document.createElement("div");
      timestamp.className = "timestamp";
      timestamp.innerText = mensaje.fecha || "Sin fecha";

      div.appendChild(remitente);
      div.appendChild(contenido);
      div.appendChild(timestamp);

      chatArea.appendChild(div);
    });
  } catch (error) {
    console.error("❌ Error al cargar el chat:", error);
    const chatArea = document.getElementById("chat-area");
    chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
  }
}

// Nueva implementación: Manejo de contactos y carga inicial
document.addEventListener("DOMContentLoaded", function () {
    const contactos = document.querySelectorAll(".contacto");
    const chatArea = document.getElementById("chat-area");

    contactos.forEach((item) => {
        // Agregar evento onclick directamente al render de los contactos
        item.addEventListener("click", () => seleccionarContacto(item.getAttribute("data-numero")));
    });

    async function seleccionarContacto(numero) {
        localStorage.setItem("numeroActivo", numero); // Guardar el número del contacto seleccionado
        cargarChat(numero); // Cargar el historial del contacto
    }

    document.getElementById("cargar-mas").addEventListener("click", async () => {
        offset += 20;
        const res = await fetch(`/api/chat/${numeroActual}?offset=${offset}`);
        const data = await res.json();

        if (data.mensajes && data.mensajes.length) {
            historial = [...data.mensajes, ...historial]; // prepend
            renderizarMensajes(historial, data.contacto);
        } else {
            alert("No hay más historial disponible.");
            document.getElementById("cargar-mas").style.display = "none";
        }
    });

    function actualizarInfoContacto(contacto, resumen) {
        document.getElementById("nombre-contacto").innerText = contacto.nombre || "Sin nombre";
        document.getElementById("numero-contacto").innerText = contacto.telefono || "";
        document.getElementById("resumen-contacto").innerText = resumen || "Sin resumen aún.";
    }

    // Agregar evento para enviar mensajes
    document.querySelector(".form-envio").addEventListener("submit", enviarMensaje);

    // Permitir agregar etiqueta al presionar Enter
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

    renderizarContactos();
});

// Función para renderizar etiquetas
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

// Función para eliminar una etiqueta
function eliminarEtiqueta(event, telefono, etiqueta) {
    event.stopPropagation(); // evitar seleccionar contacto por error

    fetch(`/api/etiqueta/${telefono}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ etiqueta })
    }).then(res => {
        if (res.ok) {
            seleccionarContacto(telefono); // recargar datos del contacto
        }
    });
}

// Función para agregar una etiqueta
function agregarEtiqueta(telefono) {
    const input = document.getElementById("nueva-etiqueta");
    const etiqueta = input.value.trim().toLowerCase();
    if (!etiqueta) return;

    fetch(`/api/etiqueta/${telefono}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ etiqueta })
    }).then(res => {
        if (res.ok) {
            seleccionarContacto(telefono); // recargar para mostrar nueva etiqueta
            input.value = "";
        }
    });
}

// Función para renderizar contactos
function renderizarContactos(contactos) {
  const listaContactos = document.getElementById("lista-contactos");
  listaContactos.innerHTML = ""; // Limpiar la lista

  contactos.forEach(contacto => {
    const li = document.createElement("li");
    li.className = "contacto-item";
    li.setAttribute("data-numero", contacto.telefono);

    li.innerHTML = `
      <div>
        <strong class="contacto-nombre">${contacto.nombre || `Usuario ${contacto.telefono.slice(-10)}`}</strong>
        <div class="contacto-telefono">${contacto.telefono.slice(-10)}</div>
      </div>
    `;

    li.addEventListener("click", () => seleccionarContacto(contacto.telefono));
    listaContactos.appendChild(li);
  });
}

// Nueva implementación de seleccionarContacto
function seleccionarContacto(telefono) {
    localStorage.setItem("numeroActivo", telefono); // Guardar el número del contacto seleccionado
    cargarChat(telefono); // Cargar el historial del contacto
}

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
}

// Nueva implementación de enviarMensaje
async function enviarMensaje(event) {
  event.preventDefault(); // Evitar recargar la página

  const input = document.getElementById("mensaje-input");
  const mensaje = input.value.trim();
  if (!mensaje) return; // No enviar mensajes vacíos

  const telefono = localStorage.getItem("numeroActivo"); // Número del contacto seleccionado
  if (!telefono) {
    console.error("❌ No se ha seleccionado un contacto.");
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
      console.error("❌ Error al enviar mensaje:", data.error);
    }
  } catch (err) {
    console.error("❌ Error en la solicitud:", err);
  }
}