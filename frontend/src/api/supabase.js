const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.replace(/\/$/, "");
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const isSupabaseConfigured = Boolean(
  supabaseUrl &&
    anonKey &&
    !supabaseUrl.includes("your-project-id") &&
    !anonKey.includes("your-supabase-anon-key")
);

const configurationError = () =>
  new Error("Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.");

const sessionToken = () => {
  try {
    return JSON.parse(localStorage.getItem("thethirdeye_session") || "null")?.access_token;
  } catch {
    return null;
  }
};

export async function supabaseRequest(path, options = {}) {
  if (!isSupabaseConfigured) throw configurationError();
  const token = sessionToken();
  const response = await fetch(`${supabaseUrl}${path}`, {
    ...options,
    headers: {
      apikey: anonKey,
      Authorization: `Bearer ${token || anonKey}`,
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Supabase request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

export const fetchAlerts = () =>
  supabaseRequest("/rest/v1/threat_alerts?select=*&order=created_at.desc&limit=250");

export const fetchBotMetrics = () =>
  supabaseRequest("/rest/v1/bot_metrics?select=*&order=last_heartbeat.desc");

export async function getUser(accessToken) {
  return supabaseRequest("/auth/v1/user", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export const signOut = () => supabaseRequest("/auth/v1/logout", { method: "POST" });

export function beginOAuth(provider) {
  if (!isSupabaseConfigured) throw configurationError();
  const redirectTo = `${window.location.origin}/login`;
  window.location.assign(
    `${supabaseUrl}/auth/v1/authorize?provider=${encodeURIComponent(provider)}&redirect_to=${encodeURIComponent(redirectTo)}`
  );
}
