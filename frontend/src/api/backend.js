const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000/api";

export async function switchMode(mode) {
  const response = await fetch(`${API_BASE_URL}/mode/switch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ mode }),
  });
  if (!response.ok) {
    throw new Error("Failed to switch mode");
  }
  return response.json();
}

export async function getMode() {
  const response = await fetch(`${API_BASE_URL}/mode`);
  if (!response.ok) {
    throw new Error("Failed to get mode");
  }
  return response.json();
}

export async function logAlertToBlockchain(alertId) {
  const response = await fetch(`${API_BASE_URL}/blockchain/log/${alertId}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to log alert to blockchain");
  }
  return response.json();
}

export async function verifyAlertOnBlockchain(alertId) {
  const response = await fetch(`${API_BASE_URL}/blockchain/verify/${alertId}`);
  if (!response.ok) {
    throw new Error("Failed to verify alert on blockchain");
  }
  return response.json();
}

export async function sendTestNotification(email, provider = "console", severity = "HIGH") {
  const response = await fetch(`${API_BASE_URL}/notifications/test`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, provider, severity }),
  });
  if (!response.ok) {
    throw new Error("Failed to send test notification");
  }
  return response.json();
}
