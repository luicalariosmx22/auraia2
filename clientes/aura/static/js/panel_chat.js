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

function cargarChat(telefono) {
    fetch(`/api/chat/${telefono}`)
        .then(response => response.json())
        .then(data => {
            console.log("Datos del chat:", data);
            if (data.success) {
                mostrarMensajes(data.mensajes);
            } else {
                console.error("Error al cargar el chat:", data.error);
            }
        })
        .catch(error => console.error("Error al cargar el chat:", error));
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