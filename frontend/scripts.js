/* =====================================================
   Team Task Manager — Shared Client-Side JavaScript
   ===================================================== */

const API_BASE = "http://localhost:5000/api";

/* ---------- Auth Helpers ---------- */
const Auth = {
  getToken: () => localStorage.getItem("ttm_token"),
  getUser:  () => JSON.parse(localStorage.getItem("ttm_user") || "null"),
  isAdmin:  () => Auth.getUser()?.role === "Admin",

  setSession(token, user) {
    localStorage.setItem("ttm_token", token);
    localStorage.setItem("ttm_user", JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem("ttm_token");
    localStorage.removeItem("ttm_user");
  },

  requireAuth() {
    if (!Auth.getToken()) {
      window.location.href = "login.html";
      return false;
    }
    return true;
  },

  requireGuest() {
    if (Auth.getToken()) {
      window.location.href = "dashboard.html";
      return false;
    }
    return true;
  },
};

/* ---------- API Client ---------- */
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await resp.json().catch(() => ({}));

  if (resp.status === 401) {
    Auth.clearSession();
    window.location.href = "login.html";
    return null;
  }

  return { ok: resp.ok, status: resp.status, data };
}

/* ---------- Toast ---------- */
const Toast = {
  container: null,

  init() {
    this.container = document.createElement("div");
    this.container.className = "toast-container";
    document.body.appendChild(this.container);
  },

  show(msg, type = "info", duration = 3500) {
    if (!this.container) this.init();
    const icons = { success: "✅", error: "❌", info: "ℹ️" };
    const t = document.createElement("div");
    t.className = `toast toast-${type}`;
    t.innerHTML = `<span>${icons[type] || ""}</span><span>${msg}</span>`;
    this.container.appendChild(t);
    setTimeout(() => t.remove(), duration);
  },

  success: (msg) => Toast.show(msg, "success"),
  error:   (msg) => Toast.show(msg, "error"),
  info:    (msg) => Toast.show(msg, "info"),
};

/* ---------- UI Helpers ---------- */
function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function statusBadge(status) {
  const map = {
    "Todo":        "badge-todo",
    "In Progress": "badge-progress",
    "Done":        "badge-done",
  };
  return `<span class="badge ${map[status] || 'badge-todo'}">${status}</span>`;
}

function overdueBadge() {
  return `<span class="badge badge-overdue">⚠ Overdue</span>`;
}

function roleBadge(role) {
  return `<span class="badge ${role === "Admin" ? "badge-admin" : "badge-member"}">${role}</span>`;
}

function setLoading(btn, loading) {
  if (loading) {
    btn.dataset.original = btn.innerHTML;
    btn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span>';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.original || btn.innerHTML;
    btn.disabled = false;
  }
}

/* ---------- Sidebar active link ---------- */
function initSidebar() {
  const currentPage = window.location.pathname.split("/").pop();
  document.querySelectorAll(".nav-item[data-page]").forEach(item => {
    if (item.dataset.page === currentPage) item.classList.add("active");
    item.addEventListener("click", () => {
      window.location.href = item.dataset.page;
    });
  });

  // Fill user info in sidebar
  const user = Auth.getUser();
  if (user) {
    const nameEl  = document.getElementById("sidebar-user-name");
    const roleEl  = document.getElementById("sidebar-user-role");
    const avatarEl = document.getElementById("sidebar-avatar");
    if (nameEl) nameEl.textContent = user.name;
    if (roleEl) roleEl.textContent = user.role;
    if (avatarEl) avatarEl.textContent = user.name.charAt(0).toUpperCase();
  }

  const logoutBtn = document.getElementById("btn-logout");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      Auth.clearSession();
      window.location.href = "login.html";
    });
  }
}

/* ---------- Modal helpers ---------- */
function openModal(id)  { document.getElementById(id).classList.add("show"); }
function closeModal(id) { document.getElementById(id).classList.remove("show"); }

// Close modal when clicking overlay
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("show");
  }
});
