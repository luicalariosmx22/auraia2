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
        numeroActual = numero;
        localStorage.setItem("numeroActivo", numero); // Guardar el número activo en localStorage
        offset = 0;
        const response = await fetch(`/api/chat/${numero}`);
        const data = await response.json();

        const chatArea = document.getElementById("chat-area");
        chatArea.innerHTML = ""; // Limpiar

        if (!data.success || !data.mensajes) {
            chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
            return;
        }

        historial = data.mensajes || [];
        renderizarMensajes(data.mensajes, data.contacto);
        actualizarInfoContacto(data.contacto, data.resumen_ia);
        document.getElementById("cargar-mas").style.display = "block";
    } catch (error) {
        console.error("Error al cargar el chat:", error);
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
        numeroActual = numero;
        localStorage.setItem("numeroActivo", numero); // Guardar el número activo en localStorage
        offset = 0;
        const res = await fetch(`/api/chat/${numero}`);
        const data = await res.json();

        if (!data.success) {
            chatArea.innerHTML = "<p class='error'>❌ No se pudo cargar el historial.</p>";
            return;
        }

        historial = data.mensajes || [];
        renderizarMensajes(data.mensajes, data.contacto);
        actualizarInfoContacto(data.contacto, data.resumen_ia);
        document.getElementById("cargar-mas").style.display = "block";

        // Renderizar etiquetas
        renderizarEtiquetas(data.contacto.etiquetas || [], numero);
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
    document.querySelector(".form-envio").addEventListener("submit", function (e) {
        e.preventDefault();

        const input = this.querySelector("input[name='mensaje']");
        const mensaje = input.value.trim();
        if (!mensaje) return;

        const numero = localStorage.getItem("numeroActivo");

        fetch("/api/enviar-mensaje", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ numero, mensaje })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                input.value = "";
                cargarChat(numero); // Recargar el chat automáticamente
            }
        })
        .catch(err => console.error("❌ Error al enviar el mensaje:", err));
    });

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
function renderizarContactos() {
    const contenedor = document.getElementById("lista-contactos");
    contenedor.innerHTML = "";

    contactos.forEach((c, i) => {
        const li = document.createElement("li");
        li.className = "contacto-item" + (i === 0 ? " activo" : "");
        li.onclick = () => seleccionarContacto(c.telefono);

        li.innerHTML = `
      <div><strong>${c.nombre || c.telefono}</strong></div>
      <span class="ultimo-mensaje">${c.mensajes?.at(-1)?.mensaje || "Sin mensajes aún"}</span>
    `;
        contenedor.appendChild(li);
    });
}

// Nueva implementación de seleccionarContacto
function seleccionarContacto(telefono) {
    console.log("Contacto seleccionado:", telefono);
    fetch(`/api/chat/${telefono}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) throw new Error("No se pudo cargar el historial.");
            
            // Renderizar mensajes en el área de chat
            renderizarMensajes(data.mensajes, data.contacto);

            // Actualizar información del contacto en la columna derecha
            document.getElementById("contacto-nombre").innerText = data.contacto.nombre || telefono;
            document.getElementById("contacto-telefono").innerText = data.contacto.telefono;

            // Renderizar etiquetas
            const etiquetasBox = document.getElementById("contacto-tags");
            etiquetasBox.innerHTML = (data.contacto.etiquetas || []).map(et =>
                `<span class="tag">${et}</span>`
            ).join("");

            // Actualizar resumen IA
            document.getElementById("resumen-ia").innerText = data.resumen_ia || "Sin resumen aún.";
        })
        .catch(err => console.error("Error al cargar el historial:", err));
}

function renderizarMensajes(mensajes, contacto) {
  const chatArea = document.getElementById("chat-area");
  chatArea.innerHTML = ""; // Limpiar el área de chat

  mensajes.forEach(mensaje => {
    const div = document.createElement("div");
    div.className = `burbuja ${mensaje.emisor === "usuario" ? "usuario" : "nora"}`;

    // Mostrar el remitente
    const remitente = document.createElement("div");
    remitente.className = "remitente";
    if (mensaje.emisor === "usuario") {
      remitente.innerText = "Tú";
    } else {
      remitente.innerText = contacto.nombre || contacto.telefono; // Mostrar nombre o número
    }

    // Mostrar el timestamp
    const timestamp = document.createElement("div");
    timestamp.className = "timestamp";
    timestamp.innerText = mensaje.fecha || "Sin fecha";

    // Mostrar el contenido del mensaje
    const contenido = document.createElement("div");
    contenido.className = "contenido";
    contenido.innerText = mensaje.mensaje;

    div.appendChild(remitente);
    div.appendChild(timestamp);
    div.appendChild(contenido);

    chatArea.appendChild(div);
  });
}