(function (window, $) {
  "use strict";

  // --- Get CSRF token from cookies ---
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie("csrftoken");

  // --- Universal fetch wrapper ---
  async function apiFetch(url, options = {}) {
    const opts = Object.assign({}, options);
    opts.headers = opts.headers || {};

    const unsafeMethods = ["POST", "PUT", "PATCH", "DELETE"];
    if (unsafeMethods.includes((opts.method || "GET").toUpperCase())) {
      opts.headers["X-CSRFToken"] = csrftoken;
    }

    if (opts.json) {
      opts.body = JSON.stringify(opts.json);
      opts.headers["Content-Type"] = "application/json";
      delete opts.json;
    }

    try {
      const res = await fetch(url, opts);
      const ct = res.headers.get("content-type") || "";
      const data = ct.includes("application/json") ? await res.json() : await res.text();
      if (!res.ok) {
        const err = new Error(`HTTP Error ${res.status}`);
        err.status = res.status;
        err.payload = data;
        throw err;
      }
      return data;
    } catch (err) {
      console.error("API Fetch failed:", err);
      alert("Something went wrong. Please try again.");
      throw err;
    }
  }

  window.getCookie = getCookie;
  window.csrftoken = csrftoken;
  window.apiFetch = apiFetch;

  // ======================
  // Chart Manager
  // ======================
  window.dashboardCharts = {};

  function initChart(canvasId, config) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    const ctx = el.getContext("2d");
    if (window.dashboardCharts[canvasId]) {
      window.dashboardCharts[canvasId].destroy();
    }
    window.dashboardCharts[canvasId] = new Chart(ctx, config);
  }

  window.initChart = initChart;

  // ======================
  // DOM ready actions
  // ======================
  $(document).ready(function () {
    // ---- Profile image preview ----
    const profileInput = document.getElementById("profile-input");
    const profileImg = document.getElementById("profile-img");
    if (profileInput && profileImg) {
      profileInput.addEventListener("change", function () {
        if (this.files && this.files[0]) {
          const reader = new FileReader();
          reader.onload = function (e) {
            profileImg.src = e.target.result;
          };
          reader.readAsDataURL(this.files[0]);
        }
      });
    }

    // ---- Branch users AJAX ----
    const branchUsersUrl = window.branchUsersUrl || "";
    function loadUsers(page = 1, query = "") {
      if (!branchUsersUrl) return;
      $.ajax({
        url: branchUsersUrl,
        data: { page, q: query },
        headers: { "X-Requested-With": "XMLHttpRequest" },
        success: function (data) {
          $("#users-container").html($(data).find("#users-container").html());
        },
        error: function () {
          console.error("Failed to load users.");
        },
      });
    }

    $("#search-box").on("keyup", function () {
      const query = $(this).val();
      loadUsers(1, query);
    });

    $(document).on("click", ".pagination a", function (e) {
      e.preventDefault();
      const page = $(this).data("page");
      const query = $("#search-box").val();
      loadUsers(page, query);
    });

    // Initial load
    loadUsers();
  });

  // ======================
  // Logout
  // ======================
  window.logout = async function () {
    try {
      const resp = await fetch("/accounts/logout/", {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
      });
      if (resp.ok) location.href = "/";
      else alert("Logout failed");
    } catch (err) {
      console.error("Logout error:", err);
      alert("Logout failed due to network error.");
    }
  };

  // ======================
  // Load profile
  // ======================
  window.loadProfile = async function () {
    try {
      const data = await apiFetch("/accounts/profile/");
      const container = document.getElementById("profile-container");
      if (container) container.innerHTML = data.html || data;
    } catch (err) {
      console.error("Failed to load profile:", err);
    }
  };
})(window, jQuery);


// ======================
// Payment methods chart
// ======================
document.addEventListener("DOMContentLoaded", function () {
  const datasetEl = document.getElementById("payment-data");
  const chartEl = document.getElementById("paymentMethodsChart");

  if (datasetEl && chartEl) {
    const cash = parseFloat(datasetEl.dataset.cash || "0");
    const card = parseFloat(datasetEl.dataset.card || "0");
    const mixed = parseFloat(datasetEl.dataset.mixed || "0");

    const ctx = chartEl.getContext("2d");
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Cash", "Card", "Mixed"],
        datasets: [
          {
            data: [cash, card, mixed],
            backgroundColor: ["#3b82f6", "#10b981", "#f59e0b"],
            borderColor: "#fff",
            borderWidth: 2,
          },
        ],
      },
    });
  }
});
