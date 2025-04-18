console.log("✅ panel_chat.js cargado correctamente");

let contactoActual = null;

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
        chatArea.innerHTML = ""; // Limpiar

        if (!data.success || !data.mensajes) {
            chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
            return;
        }

        data.mensajes.forEach(m => {
            const burbuja = document.createElement("div");
            burbuja.classList.add("burbuja");
            burbuja.classList.add(m.emisor === "bot" ? "nora" : "usuario");

            const hora = document.createElement("span");
            hora.classList.add("hora");
            hora.innerText = m.hora.slice(11, 16); // solo HH:MM

            burbuja.innerText = m.mensaje;
            burbuja.appendChild(hora);
            chatArea.appendChild(burbuja);
        });

        // También actualiza los detalles del contacto a la derecha
        document.getElementById("nombre-contacto").innerText = data.contacto.nombre;
        document.getElementById("numero-contacto").innerText = data.contacto.telefono;
        document.getElementById("resumen-contacto").innerText = data.resumen_ia || "Sin resumen.";
    } catch (error) {
        console.error("Error al cargar el chat:", error);
        const chatArea = document.getElementById("chat-area");
        chatArea.innerHTML = "<p>Error al cargar el historial.</p>";
    }
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