import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("gs_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export type ChatMessage = {
  id?: string;
  role: "user" | "assistant";
  content: string;
  is_emergency?: boolean;
};

export async function sendChatMessage(
  message: string,
  conversationId: string | null,
  language: string = "auto",
  coords?: { lat: number; lon: number }
) {
  const { data } = await api.post("/chat", {
    message,
    conversation_id: conversationId,
    language,
    latitude: coords?.lat,
    longitude: coords?.lon,
  });
  return data;
}

export async function fetchConversations() {
  const { data } = await api.get("/chat/conversations");
  return data;
}

export async function fetchNearbyHospitals(lat: number, lon: number) {
  const { data } = await api.get("/hospitals/nearby", { params: { lat, lon } });
  return data;
}

export async function login(payload: { email?: string; phone?: string; password: string }) {
  const { data } = await api.post("/auth/login", payload);
  return data;
}

export async function signup(payload: {
  name: string;
  email?: string;
  phone?: string;
  password: string;
}) {
  const { data } = await api.post("/auth/signup", payload);
  return data;
}

export async function fetchMe() {
  const { data } = await api.get("/auth/me");
  return data;
}
