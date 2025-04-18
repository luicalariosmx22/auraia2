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
    contactoActual = telefono;
    fetch(`/api/chat/${telefono}`)
        .then(response => response.json())
        .then(data => {
            console.log("Datos del chat:", data);
            if (data.success) {
                mostrarMensajes(data.mensajes);
                mostrarInfoContacto(data.contacto);
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

// Funciones nuevas integradas
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