import { postJSON } from "./tareas_utils.js";

export function initToggleRecurrencia() {
  const recCheck = document.getElementById("recurrente_checkbox");
  const recFields = document.getElementById("campos_recurrencia");
  if (!recCheck || !recFields) return;

  recCheck.addEventListener("change", e => {
    recFields.classList.toggle("hidden", !e.target.checked);
  });

  const rruleType = document.getElementById("rrule_type");
  const dtstartInput = document.getElementById("fecha_inicio");
  const preview = document.getElementById("rrule_preview");

  function updateRRule() {
    const freq = (rruleType.value || "").toUpperCase();
    if (!freq) {
      preview.value = "";
      return;
    }
    let rule = `FREQ=${freq}`;
    if (freq === "WEEKLY" && dtstartInput.value) {
      const days = ["SU","MO","TU","WE","TH","FR","SA"];
      const d = new Date(dtstartInput.value);
      rule += `;BYDAY=${days[d.getUTCDay()]}`;
    } else if (freq === "MONTHLY" && dtstartInput.value) {
      const day = new Date(dtstartInput.value).getUTCDate();
      rule += `;BYMONTHDAY=${day}`;
    }
    preview.value = rule;
  }

  rruleType?.addEventListener("change", updateRRule);
  dtstartInput?.addEventListener("change", updateRRule);
}

export function initModalNuevaTareaSubmit() {
  const form = document.getElementById("formTarea");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {};
    const formData = new FormData(form);
    formData.forEach((val, key) => {
      if (val) payload[key] = val;
    });

    console.log("🧪 Payload a enviar:", payload);

    const nombreNora = document.body.getAttribute("data-nora");
    const res = await postJSON(`/panel_cliente/${nombreNora}/tareas/gestionar/crear`, payload);

    if (res.ok) location.reload();
  });
}
