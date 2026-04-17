const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  getHealth: () => request("/healthz"),
  getApiRoot: () => request("/"),
  listWatchlist: () => request("/watchlist"),
  addWatchlistItem: (payload) =>
    request("/watchlist", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteWatchlistItem: (symbol) =>
    request(`/watchlist/${encodeURIComponent(symbol)}`, {
      method: "DELETE",
    }),
  getPriceSnapshot: (symbol) => request(`/prices/${encodeURIComponent(symbol)}`),
  listAlerts: (limit = 10) => request(`/alerts?limit=${limit}`),
  refreshWatchlist: () =>
    request("/refresh", {
      method: "POST",
    }),
  forceBreach: (payload) =>
    request("/dev/force-breach", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  resetDemoState: (payload) =>
    request("/dev/reset", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
