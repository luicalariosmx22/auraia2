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
        renderizarMensajes(historial);
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
        item.addEventListener("click", () => {
            const numero = item.getAttribute("data-numero");
            const nombre = item.getAttribute("data-nombre");
            seleccionarContacto(nombre, numero);
        });
    });

    async function seleccionarContacto(nombre, numero) {
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
        renderizarMensajes(historial);
        actualizarInfoContacto(data.contacto, data.resumen_ia);
        document.getElementById("cargar-mas").style.display = "block";
    }

    document.getElementById("cargar-mas").addEventListener("click", async () => {
        offset += 20;
        const res = await fetch(`/api/chat/${numeroActual}?offset=${offset}`);
        const data = await res.json();

        if (data.mensajes && data.mensajes.length) {
            historial = [...data.mensajes, ...historial]; // prepend
            renderizarMensajes(historial);
        } else {
            alert("No hay más historial disponible.");
            document.getElementById("cargar-mas").style.display = "none";
        }
    });

    function renderizarMensajes(mensajes) {
        chatArea.innerHTML = ""; // limpia

        mensajes.forEach((msg) => {
            const burbuja = document.createElement("div");
            burbuja.classList.add("burbuja", msg.emisor === "bot" ? "nora" : "usuario");

            const texto = document.createElement("p");
            texto.innerText = msg.mensaje;
            burbuja.appendChild(texto);

            const hora = document.createElement("span");
            hora.classList.add("hora");
            hora.innerText = msg.hora?.slice(11, 16) || "";
            burbuja.appendChild(hora);

            chatArea.appendChild(burbuja);
        });

        chatArea.scrollTop = chatArea.scrollHeight;
    }

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
});

// Funciones adicionales...
function enviarMensaje(e) {
    e.preventDefault();
    const input = document.getElementById("mensaje");
    const texto = input.value.trim();
    if (!texto || !contactoActual) return;

    const botonEnviar = document.getElementById("boton-enviar");
    botonEnviar.disabled = true;

    fetch("/api/enviar-mensaje", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            numero: contactoActual,
            mensaje: texto,
            nombre_nora: nombreNora
        })
    })
        .then(res => {
            if (!res.ok) throw new Error("Error al enviar el mensaje");
            return res.json();
        })
        .then(() => {
            input.value = "";
            cargarChat(contactoActual);
        })
        .catch(err => manejarError(err, "Error al enviar el mensaje."))
        .finally(() => {
            botonEnviar.disabled = false;
        });
}

function filtrarContactosPorEtiqueta(etiqueta) {
    const lista = document.getElementById("lista-contactos").children;
    for (let li of lista) {
        const etiquetas = li.dataset.etiquetas.toLowerCase();
        li.style.display = etiqueta && !etiquetas.includes(etiqueta.toLowerCase()) ? "none" : "";
    }
}

function filtrarContactosPorNombre(texto) {
    const lista = document.getElementById("lista-contactos").children;
    const t = texto.toLowerCase();
    for (let li of lista) {
        const nombre = li.querySelector(".nombre").innerText.toLowerCase();
        const numero = li.querySelector(".numero").innerText.toLowerCase();
        li.style.display = nombre.includes(t) || numero.includes(t) ? "" : "none";
    }
}

function mostrarInfoContacto(contacto) {
    document.getElementById("info-contacto").style.display = "none";
    const detalles = document.getElementById("detalles-contacto");
    detalles.style.display = "block";

    document.getElementById("nombre-contacto").innerText = contacto.nombre;
    document.getElementById("numero-contacto").innerText = contacto.numero;
    document.getElementById("btn-toggle-ia").innerText = contacto.ia ? "Desactivar IA" : "Activar IA";

    // Mostrar etiquetas
    const contenedor = document.getElementById("etiquetas-contacto");
    contenedor.innerHTML = "";
    if (contacto.etiquetas && contacto.etiquetas.length > 0) {
        contacto.etiquetas.forEach(et => {
            const span = document.createElement("span");
            span.className = "badge";
            span.innerText = et;
            contenedor.appendChild(span);
        });
    } else {
        contenedor.innerHTML = "<span class='badge badge-muted'>Sin etiquetas</span>";
    }

    // Mostrar notas
    document.getElementById("notas-contacto").value = contacto.nota || "";

    // Mostrar resumen
    document.getElementById("resumen-contacto").innerText = contacto.resumen || "Sin resumen disponible.";
}

function agregarEtiqueta(event) {
    event.preventDefault();
    const nueva = document.getElementById("nueva-etiqueta").value.trim();
    if (!nueva) return;
    const numero = document.getElementById("numero-contacto").innerText;

    fetch(`/api/etiquetas/agregar/${numero}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ etiqueta: nueva })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            cargarChat(numero); // Recarga contacto con nueva etiqueta
        }
    });
}

function guardarNota() {
    const nota = document.getElementById("notas-contacto").value;
    const numero = document.getElementById("numero-contacto").innerText;

    fetch(`/api/notas/${numero}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nota })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("✅ Nota guardada");
        }
    });
}

function toggleIAContacto() {
    const numero = document.getElementById("numero-contacto").innerText;
    fetch(`/api/toggle-ia/${numero}`, { method: "POST" })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById("btn-toggle-ia").innerText = data.activa ? "Desactivar IA" : "Activar IA";
            alert(`IA ${data.activa ? "activada" : "desactivada"} para este contacto`);
        }
    });
}