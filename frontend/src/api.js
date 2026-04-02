const API = "";

async function request(path, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = { ...options.headers };

  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API}${path}`, { ...options, headers });

  if (res.status === 401) {
    const refreshed = await tryRefresh();
    if (refreshed) return request(path, options);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(
      Array.isArray(err.detail)
        ? err.detail.map((e) => e.msg).join(", ")
        : err.detail || "Request failed"
    );
  }

  return res.json();
}

let refreshing = null;
async function tryRefresh() {
  if (refreshing) return refreshing;
  const rt = localStorage.getItem("refresh_token");
  if (!rt) return false;
  refreshing = (async () => {
    try {
      const res = await fetch(`${API}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: rt }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      return true;
    } catch {
      return false;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

export const auth = {
  login: (username, password) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return fetch(`${API}/auth/login`, { method: "POST", body: form }).then(
      async (res) => {
        if (!res.ok) throw new Error("Invalid credentials");
        return res.json();
      }
    );
  },
  register: (data) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  me: () => request("/auth/me"),
};

export const problems = {
  list: (skip = 0, limit = 50) =>
    request(`/problems?skip=${skip}&limit=${limit}`),
  get: (id) => request(`/problems/${id}`),
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/problems/upload", { method: "POST", body: form });
  },
  delete: (id) => request(`/problems/${id}`, { method: "DELETE" }),
};

export const submissions = {
  create: (data) =>
    request("/submissions", { method: "POST", body: JSON.stringify(data) }),
  get: (id) => request(`/submissions/${id}`),
  mine: (skip = 0, limit = 50) =>
    request(`/submissions/me?skip=${skip}&limit=${limit}`),
  byProblem: (problemId, skip = 0, limit = 50) =>
    request(
      `/submissions/problem/${problemId}?skip=${skip}&limit=${limit}`
    ),
};

export const contests = {
  list: (skip = 0, limit = 50) =>
    request(`/contests?skip=${skip}&limit=${limit}`),
  get: (id) => request(`/contests/${id}`),
  create: (data) =>
    request("/contests", { method: "POST", body: JSON.stringify(data) }),
  register: (id) => request(`/contests/${id}/register`, { method: "POST" }),
  standings: (id) => request(`/contests/${id}/standings`),
};
