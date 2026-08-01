// ---------------- Config ----------------
const API_BASE = "http://127.0.0.1:8000";

// ---------------- Elements ----------------
const historyList = document.getElementById("history-list");
const emptyState = document.getElementById("empty-state");
const errorBanner = document.getElementById("error-banner");

const detailPanel = document.getElementById("detail-panel");
const detailTopic = document.getElementById("detail-topic");
const detailReport = document.getElementById("detail-report");
const detailFeedback = document.getElementById("detail-feedback");
const backBtn = document.getElementById("back-btn");

// ---------------- Helpers ----------------
function showError(message) {
  errorBanner.textContent = message;
  errorBanner.classList.remove("hidden");
  setTimeout(() => errorBanner.classList.add("hidden"), 5000);
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ---------------- Load history list ----------------
async function loadHistory() {
  // Show skeleton placeholders while loading
  historyList.innerHTML = `
    <div class="skeleton-row"></div>
    <div class="skeleton-row"></div>
    <div class="skeleton-row"></div>
  `;

  try {
    const response = await fetch(`${API_BASE}/history`);
    if (!response.ok) throw new Error("Failed to load history.");

    const reports = await response.json();
    historyList.innerHTML = "";

    if (!reports || reports.length === 0) {
      emptyState.classList.remove("hidden");
      return;
    }

    emptyState.classList.add("hidden");

    reports.forEach((r) => {
      const row = document.createElement("div");
      row.className = "history-row";
      row.innerHTML = `
        <span class="history-row-topic">${escapeHTML(r.topic)}</span>
        <span class="history-row-date">${formatDate(r.created_at)}</span>
      `;
      row.addEventListener("click", () => loadReportDetail(r.id));
      historyList.appendChild(row);
    });

  } catch (err) {
    historyList.innerHTML = "";
    showError(err.message || "Could not reach the server. Is the backend running?");
  }
}

// ---------------- Load a single report ----------------
async function loadReportDetail(id) {
  try {
    const response = await fetch(`${API_BASE}/report/${id}`);
    if (!response.ok) throw new Error("Report not found.");

    const data = await response.json();

    detailTopic.textContent = data.topic;
    detailReport.innerHTML = renderMarkdown(data.report || "");

    const score = extractScore(data.feedback);
    const scoreHTML = score !== null
      ? `<div class="score-display"><span class="score-number">${score}</span><span class="score-max">/ 10</span></div>`
      : "";
    detailFeedback.innerHTML = scoreHTML + renderMarkdown(data.feedback || "");

    document.querySelector(".history-panel").classList.add("hidden");
    document.querySelector(".history-hero").classList.add("hidden");
    detailPanel.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });

  } catch (err) {
    showError(err.message || "Could not load this report.");
  }
}

backBtn.addEventListener("click", () => {
  detailPanel.classList.add("hidden");
  document.querySelector(".history-panel").classList.remove("hidden");
  document.querySelector(".history-hero").classList.remove("hidden");
});

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------- Init ----------------
loadHistory();