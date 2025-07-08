// Función para enviar datos como FormData y manejar respuesta JSON
export async function postJSON(url, payload = {}) {
  const formData = new FormData();
  for (const key in payload) {
    if (payload[key] !== undefined && payload[key] !== null) {
      formData.append(key, payload[key]);
    }
  }
  const res = await fetch(url, {
    method: "POST",
    body: formData
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) {
    throw new Error(data.error || res.statusText);
  }
  return data;
}
