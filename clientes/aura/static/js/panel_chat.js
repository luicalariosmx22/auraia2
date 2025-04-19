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
        renderizarMensajes(historial);
        actualizarInfoContacto(data.contacto, data.resumen_ia);
        document.getElementById("cargar-mas").style.display = "block";

        // Renderizar etiquetas con botones de agregar y eliminar
        const etiquetasContainer = document.getElementById("lista-etiquetas-editable");
        etiquetasContainer.innerHTML = (data.contacto.etiquetas || []).map(et =>
            `<span class="tag">
                ${et} <button onclick="eliminarEtiqueta('${numero}', '${et}')">x</button>
            </span>`
        ).join("");
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

    // Función para agregar etiquetas
    function agregarEtiqueta(telefono, etiqueta) {
        fetch(`/api/etiqueta/${telefono}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ etiqueta })
        }).then(() => seleccionarContacto(telefono));
    }

    // Función para eliminar etiquetas
    function eliminarEtiqueta(telefono, etiqueta) {
        fetch(`/api/etiqueta/${telefono}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ etiqueta })
        }).then(() => seleccionarContacto(telefono));
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