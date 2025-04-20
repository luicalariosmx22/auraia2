document.addEventListener("DOMContentLoaded", () => {
  const filtrosForm = document.querySelector("#filtros-form");
  const contactosTableBody = document.querySelector("#contactos-tbody");

  // Escuchar el evento de envío del formulario
  filtrosForm.addEventListener("submit", (event) => {
    event.preventDefault(); // Evitar recargar la página

    // Obtener los valores de los filtros
    const busqueda = document.querySelector('input[name="busqueda"]').value.trim();
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value;
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value;
    const etiqueta = document.querySelector('select[name="etiqueta"]').value;
    const nombreNora = "nombreNora"; // Definir el nombreNora según sea necesario

    // Enviar la solicitud AJAX al servidor
    fetch(`/panel_cliente/contactos/${nombreNora}?busqueda=${busqueda}&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&etiqueta=${etiqueta}`, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest", // Indicar que es una solicitud AJAX
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Error en la solicitud: ${response.statusText}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.success) {
          // Actualizar la tabla con los contactos recibidos
          actualizarTablaContactos(data.contactos);
        } else {
          alert("Error al cargar los contactos: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Error al cargar los contactos:", error);
      });
  });

  // Función para actualizar la tabla de contactos
  function actualizarTablaContactos(contactos) {
    const contactosTableBody = document.querySelector("#contactos-tbody");
    contactosTableBody.innerHTML = ""; // Limpiar la tabla

    contactos.forEach((contacto) => {
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
        <td>${contacto.ultimo_mensaje ? contacto.ultimo_mensaje.slice(0, 10) : "N/A"}</td>
        <td>
          <a href="/contactos/editar/${contacto.telefono}">✏️ Editar</a>
          <button onclick="eliminarContacto('${contacto.telefono}')">🗑️ Eliminar</button>
        </td>
      `;
      contactosTableBody.appendChild(row);
    });
  }
});