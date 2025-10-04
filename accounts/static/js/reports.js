// accounts/static/js/reports.js
let salesChart = null;
let topItemsChart = null;

// Helper - safely read branch id from page (body data attribute)
function getBranchId() {
  try {
    const b = document.body.dataset.branchId;
    return b ? String(b) : null;
  } catch (e) {
    return null;
  }
}

// Build URL adding branch_id when available
function buildUrl(path, params = {}) {
  const branchId = getBranchId();
  const url = new URL(path, window.location.origin);
  if (branchId) url.searchParams.set("branch_id", branchId);
  for (const k in params) {
    if (params[k] !== undefined && params[k] !== null) {
      url.searchParams.set(k, params[k]);
    }
  }
  return url.toString();
}

// Render chart helper
function renderChart(canvasId, data, label) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // Destroy previous instance
  if (canvasId === "salesChart" && salesChart) {
    try { salesChart.destroy(); } catch (e) {}
  }
  if (canvasId === "topItemsChart" && topItemsChart) {
    try { topItemsChart.destroy(); } catch (e) {}
  }

  const chartType = canvasId === "topItemsChart" ? "bar" : "line";
  const cfg = {
    type: chartType,
    data: {
      labels: data.labels || [],
      datasets: [{
        label: label,
        data: data.totals || [],
        borderColor: "rgb(54, 162, 235)",
        backgroundColor: chartType === "bar"
          ? "rgba(54, 162, 235, 0.6)"
          : "rgba(54, 162, 235, 0.12)",
        tension: 0.2,
        fill: chartType !== "bar"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true, position: "top" },
        tooltip: { mode: "index", intersect: false }
      },
      interaction: { mode: 'nearest', axis: 'x', intersect: false },
      scales: {
        x: { display: true },
        y: { display: true, beginAtZero: true }
      }
    }
  };

  const instance = new Chart(ctx, cfg);
  if (canvasId === "salesChart") salesChart = instance;
  else topItemsChart = instance;
}

// Load sales trends by period
async function loadTrends(period) {
  const url = buildUrl(`/reports/sales_trends/${encodeURIComponent(period)}/`);
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Network response not ok");
    const data = await res.json();
    renderChart("salesChart", data, `Sales (${period})`);
  } catch (err) {
    console.error("loadTrends error:", err);
    renderChart("salesChart", { labels: [], totals: [] }, `Sales (${period})`);
  }
}

// Load sales trends by custom date range
async function loadTrendsRange(start, end) {
  const url = buildUrl("/reports/sales_trends_range/", { start: start, end: end });
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Network response not ok");
    const data = await res.json();
    renderChart("salesChart", data, `Sales (${start} → ${end})`);
  } catch (err) {
    console.error("loadTrendsRange error:", err);
    renderChart("salesChart", { labels: [], totals: [] }, `Sales (${start} → ${end})`);
  }
}

// Load top items
async function loadTopItems() {
  const url = buildUrl("/reports/top_items/");
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Network response not ok");
    const data = await res.json();
    renderChart("topItemsChart", data, "Top Items (qty)");
  } catch (err) {
    console.error("loadTopItems error:", err);
    renderChart("topItemsChart", { labels: [], totals: [] }, "Top Items");
  }
}

// Load low stock list
async function loadLowStock() {
  const url = buildUrl("/reports/low_stock/");
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Network response not ok");
    const data = await res.json();
    const ul = document.getElementById("lowStockList");
    if (!ul) return;
    ul.innerHTML = "";
    (data.items || []).forEach(it => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.textContent = `${it.name} — Stock: ${it.stock}`;
      ul.appendChild(li);
    });
  } catch (err) {
    console.error("loadLowStock error:", err);
  }
}

// Update export links (CSV/PDF) with branch + optional dates
function updateExportLinks(start = null, end = null) {
  const csvBtn = document.getElementById("exportCsvBtn");
  const pdfBtn = document.getElementById("exportPdfBtn");
  if (!csvBtn || !pdfBtn) return;

  const params = {};
  const branchId = getBranchId();
  if (branchId) params.branch_id = branchId;
  if (start && end) { params.start = start; params.end = end; }

  const csvUrl = buildUrl("/reports/export/csv/", params);
  const pdfUrl = buildUrl("/reports/export/pdf/", params);
  csvBtn.href = csvUrl;
  pdfBtn.href = pdfUrl;
}

// Apply date filter (reads daterange input)
function applyDateFilter() {
  const inp = document.getElementById("daterange");
  if (!inp) return;
  const val = inp.value || "";
  const parts = val.split(" - ");
  if (parts.length !== 2) {
    alert("Please select a date range.");
    return;
  }
  const start = moment(parts[0], "MM/DD/YYYY").format("YYYY-MM-DD");
  const end = moment(parts[1], "MM/DD/YYYY").format("YYYY-MM-DD");
  loadTrendsRange(start, end);
  updateExportLinks(start, end);
}

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  // If moment/daterangepicker not present, datepicker init will fail — guard
  try {
    if (window.jQuery && typeof window.jQuery.fn.daterangepicker === "function") {
      $("#daterange").daterangepicker({ opens: "left" });
    }
  } catch (e) {
    // ignore
  }

  const applyBtn = document.getElementsByClassName("applyBtn")[0];
  if (applyBtn) {
    applyBtn.addEventListener("click", () => {
      setTimeout(() => {
        applyDateFilter(); 
      }, 500);
    });
  }

  // Initial loads:
  loadTrends("daily");
  loadTopItems();
  loadLowStock();
  updateExportLinks();
});
