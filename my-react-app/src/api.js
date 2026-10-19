// All communication with the FastAPI backend lives here.
const USE_MOCK = true; // change to false when the backend is running
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const MOCK_RESPONSE = {
  reply: "Based on comparable streetlight complaints in Astoria, this issue is likely to be resolved within 3–5 business days.",
  prediction: { estimate: "3–5 business days", confidence: 82 },
};

export async function sendMessage(text) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return MOCK_RESPONSE;
  }

  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res.json(); // { reply, prediction }
}