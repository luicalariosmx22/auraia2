console.log("✅ panel_chat.js cargado correctamente");

let contactoActual = null;

function mostrarError(mensaje) {
    alert(`❌ ${mensaje}`);
}

function manejarError(err, mensaje) {
    console.error(err);
    mostrarError(mensaje);
}

function mostrarMensajes(mensajes) {
    const chatArea = document.getElementById("chat-area");
    const debugChat = document.getElementById("debug-chat");
    chatArea.innerHTML = ""; // Limpia el área de chat
    debugChat.textContent = JSON.stringify(mensajes, null, 2); // Muestra los mensajes en formato JSON

    mensajes.forEach(mensaje => {
        const mensajeDiv = document.createElement("div");
        mensajeDiv.classList.add("mensaje");

        // Diferenciar entre mensajes del usuario y de Nora
        if (mensaje.emisor === "usuario") {
            mensajeDiv.classList.add("usuario");
            mensajeDiv.innerHTML = `<div class="texto">${mensaje.mensaje}</div>`;
        } else if (mensaje.emisor === "bot") {
            mensajeDiv.classList.add("nora");
            mensajeDiv.innerHTML = `<div class="texto">${mensaje.mensaje}</div>`;
        }

        chatArea.appendChild(mensajeDiv);
    });

    // Desplazar hacia abajo automáticamente
    chatArea.scrollTop = chatArea.scrollHeight;
}

function cargarChat(numero) {
    const chatArea = document.getElementById("chat-area");
    chatArea.innerHTML = '<p class="placeholder">Cargando mensajes...</p>';

    fetch(`/api/chat/${numero}`)
        .then(res => {
            if (!res.ok) throw new Error("Error al cargar el chat");
            return res.json();
        })
        .then(data => {
            contactoActual = numero;

            chatArea.innerHTML = "";

            if (!data.mensajes || data.mensajes.length === 0) {
                chatArea.innerHTML = '<p class="placeholder">Sin mensajes aún.</p>';
            } else {
                mostrarMensajes(data.mensajes);
            }

            const info = document.getElementById("info-contacto");
            const etiquetas = data.contacto.etiquetas && data.contacto.etiquetas.length > 0 ? data.contacto.etiquetas.join(", ") : "Sin etiquetas";
            const resumen = data.resumen_ia || "Sin resumen disponible.";

            info.innerHTML = `
                <h3>${data.contacto.nombre}</h3>
                <p><strong>Número:</strong> ${data.contacto.numero}</p>
                <p><strong>Etiquetas:</strong> ${etiquetas}</p>
                <p><strong>IA:</strong> ${data.contacto.ia_activada ? '🟢 Activada' : '🔴 Desactivada'}</p>
                <button onclick="toggleIA('${data.contacto.numero}')">
                    ${data.contacto.ia_activada ? 'Desactivar IA' : 'Activar IA'}
                </button>
                <hr>
                <p><strong>🧠 Resumen IA:</strong><br>${resumen}</p>
                <hr>
                <h4>📆 Programar envío</h4>
                <form onsubmit="programarEnvio(event, '${data.contacto.numero}')">
                    <textarea id="mensaje-programado" placeholder="Mensaje..." rows="3" style="width: 100%;"></textarea><br>
                    <input type="date" id="fecha-envio" required>
                    <input type="time" id="hora-envio" required>
                    <button type="submit">Programar</button>
                </form>
            `;

            chatArea.scrollTop = chatArea.scrollHeight;
        })
        .catch(err => manejarError(err, "Error al cargar el chat."));
}

function enviarMensaje(e) {
    e.preventDefault();
    const input = document.getElementById("mensaje");
    const texto = input.value.trim();
    if (!texto || !contactoActual) return;

    const botonEnviar = document.getElementById("boton-enviar");
    botonEnviar.disabled = true;

    fetch("/api/enviar-mensaje", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
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

function toggleIA(numero) {
    fetch(`/api/toggle-ia/${numero}`, { method: "POST" })
        .then(res => {
            if (!res.ok) throw new Error("Error al cambiar el estado de la IA");
            return res.json();
        })
        .then(() => cargarChat(numero))
        .catch(err => manejarError(err, "Error al cambiar el estado de la IA."));
}

function programarEnvio(e, numero) {
    e.preventDefault();
    const mensaje = document.getElementById("mensaje-programado").value.trim();
    const fecha = document.getElementById("fecha-envio").value;
    const hora = document.getElementById("hora-envio").value;

    if (!mensaje || !fecha || !hora) {
        mostrarError("Todos los campos son obligatorios.");
        return;
    }

    fetch("/api/programar-envio", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            numero,
            mensaje,
            fecha,
            hora,
            nombre_nora: nombreNora
        })
    })
    .then(res => {
        if (!res.ok) throw new Error("Error al programar el envío");
        return res.json();
    })
    .then(() => {
        alert("✅ Envío programado con éxito");
        document.getElementById("mensaje-programado").value = "";
    })
    .catch(err => manejarError(err, "Error al programar el envío."));
}