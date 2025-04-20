document.addEventListener("DOMContentLoaded", () => {
  const filtrosForm = document.querySelector("#filtros-form");
  const contactosTableBody = document.querySelector("#contactos-tbody");

  // Escuchar el evento de envío del formulario
  filtrosForm.addEventListener("submit", (event) => {
    event.preventDefault(); // Evitar recargar la página

    // Obtener los valores de los filtros
    const formData = new FormData(filtrosForm);
    const params = new URLSearchParams(formData);

    // Enviar la solicitud AJAX al servidor
    fetch(`/contactos?${params.toString()}`, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest", // Indicar que es una solicitud AJAX
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Limpiar la tabla
          contactosTableBody.innerHTML = "";

          // Agregar los contactos al cuerpo de la tabla
          data.contactos.forEach((contacto) => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${contacto.telefono}</td>
              <td>${contacto.nombre}</td>
              <td>
                ${
                  contacto.etiquetas && contacto.etiquetas.length > 0
                    ? contacto.etiquetas.map((et) => `<span class="badge">${et}</span>`).join(" ")
                    : '<span class="badge badge-muted">Sin etiquetas</span>'
                }
              </td>
              <td>${contacto.ultimo_mensaje || "N/A"}</td>
            `;
            contactosTableBody.appendChild(row);
          });
        } else {
          alert("Error al cargar los contactos: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Error al cargar los contactos:", error);
      });
  });
});