// All communication with the FastAPI backend lives here.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function parseResponse(res) {
  const data = await res.json();

  if (!res.ok) {
    const detail = data.detail;
    const message =
      typeof detail === "string"
        ? detail
        : detail?.message ?? `Request failed (${res.status})`;

    throw new Error(message);
  }

  return data;
}

export async function sendMessage(text, query = null, pending_field = null, confirmed = false) {
  const res = await fetch(`${API_URL}/api/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: text, query, pending_field, confirmed }),
  });
  return parseResponse(res);
}

export async function getPrediction(query) {
  const res = await fetch(`${API_URL}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  return parseResponse(res);
}