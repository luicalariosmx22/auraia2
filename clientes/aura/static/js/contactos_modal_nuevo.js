console.log('[DEBUG] contactos_modal_nuevo.js cargado');

// Modal y lógica para alta de nuevo contacto en panel de contactos
window.abrirModalContacto = function () {
  const modal = document.getElementById("modalNuevoContacto");
  if (modal) {
    modal.classList.remove("hidden");
  }
};

window.cerrarModalContacto = function () {
  const modal = document.getElementById("modalNuevoContacto");
  if (modal) {
    modal.classList.add("hidden");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const boton = document.getElementById("btnNuevoContacto");
  console.log('[DEBUG] DOMContentLoaded, btnNuevoContacto:', boton, typeof boton);
  if (boton) {
    boton.addEventListener("click", function() {
      console.log('[DEBUG] Click en btnNuevoContacto, abriendo modal...');
      abrirModalContacto();
    });
  } else {
    console.error('[ERROR] No se encontró el botón btnNuevoContacto en el DOM');
  }

  const form = document.getElementById("formNuevoContacto");
  console.log('[DEBUG] formNuevoContacto:', form);
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const submitBtn = form.querySelector("button[type='submit']");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Enviando...";
      }
      const formData = new FormData(form);
      // Elimina campos vacíos para evitar errores de tipo en backend/Supabase
      for (const [key, value] of formData.entries()) {
        if (typeof value === 'string' && value.trim() === '') {
          formData.delete(key);
        }
      }
      try {
        const resp = await fetch(form.action || window.location.pathname + "/nuevo_usuario", {
          method: "POST",
          body: formData
        });
        if (resp.ok) {
          cerrarModalContacto();
          window.location.reload(); // Recarga la tabla tras alta
        } else {
          alert("Error al guardar el contacto");
        }
      } catch (err) {
        alert("Error de red o servidor");
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Guardar contacto";
        }
      }
    });

    // Etiquetas: actualizar el input hidden antes de submit
    const etiquetasCheckboxes = document.querySelectorAll('.etiqueta-checkbox-nuevo');
    const etiquetasInput = document.getElementById('etiquetas_string_nuevo_contacto');
    if (form && etiquetasCheckboxes.length && etiquetasInput) {
      form.addEventListener('submit', function () {
        const seleccionadas = Array.from(etiquetasCheckboxes)
          .filter(cb => cb.checked)
          .map(cb => cb.value.trim())
          .filter(Boolean);
        etiquetasInput.value = seleccionadas.join(', ');
      });
      // UX: toggle visual badge selection
      etiquetasCheckboxes.forEach(cb => {
        cb.addEventListener('change', function () {
          const badge = this.nextElementSibling;
          if (this.checked) {
            badge.classList.add('ring', 'ring-2', 'ring-blue-400');
          } else {
            badge.classList.remove('ring', 'ring-2', 'ring-blue-400');
          }
        });
      });
    }
  }
});
