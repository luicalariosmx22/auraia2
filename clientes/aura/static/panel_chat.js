let contactoActual = null;

function cargarChat(numero) {
    fetch(`/api/chat/${numero}`)
        .then(res => res.json())
        .then(data => {
            contactoActual = numero;

            const chatArea = document.getElementById("chat-area");
            chatArea.innerHTML = "";

            data.mensajes.forEach(m => {
                const div = document.createElement("div");
                div.className = m.origen === "usuario" ? "burbuja-usuario" : "burbuja-nora";
                div.innerHTML = `<strong>${m.origen}</strong><br>${m.texto}<br><small>${m.hora}</small>`;
                chatArea.appendChild(div);
            });

            const info = document.getElementById("info-contacto");
            info.innerHTML = `
                <h3>${data.contacto.nombre}</h3>
                <p><strong>Número:</strong> ${data.contacto.numero}</p>
                <p><strong>Etiquetas:</strong> ${data.contacto.etiquetas.join(", ") || 'Sin etiquetas'}</p>
                <p><strong>IA:</strong> ${data.contacto.ia_activada ? '🟢 Activada' : '🔴 Desactivada'}</p>
                <button onclick="toggleIA('${data.contacto.numero}')">${data.contacto.ia_activada ? 'Desactivar IA' : 'Activar IA'}</button>
            `;
        });
}

function enviarMensaje(e) {
    e.preventDefault();
    const input = document.getElementById("mensaje");
    const texto = input.value.trim();
    if (!texto || !contactoActual) return;

    fetch("/api/enviar-mensaje", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            numero: contactoActual,
            mensaje: texto,
            nombre_nora: nombreNora
        })
    }).then(res => res.json())
      .then(() => {
          input.value = "";
          cargarChat(contactoActual);
      });
}

function toggleIA(numero) {
    fetch(`/api/toggle-ia/${numero}`, { method: "POST" })
        .then(() => cargarChat(numero));
}
