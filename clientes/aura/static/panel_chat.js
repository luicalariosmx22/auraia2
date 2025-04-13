function abrirChat(numero) {
    fetch(`/chat/${numero}`)
        .then(res => res.json())
        .then(data => {
            let html = `<h2>Chat con ${data.nombre}</h2>`;
            data.historial.forEach(m => {
                html += `<div><strong>${m.origen}:</strong> ${m.mensaje} <small>${m.hora}</small></div>`;
            });
            document.getElementById("chat-main").innerHTML = html;
        });
}
