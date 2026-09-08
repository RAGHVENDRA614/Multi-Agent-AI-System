// ---------------- Config ----------------
const API_BASE = "https://multi-agent-ai-system-f7q2.onrender.com";

// ---------------- Elements ----------------
const form = document.getElementById("research-form");
const topicInput = document.getElementById("topic-input");
const templateSelect = document.getElementById("template-select");
const submitBtn = document.getElementById("submit-btn");
const useCacheCheckbox = document.getElementById("use-cache");
const micBtn = document.getElementById("mic-btn");

const resultPanel = document.getElementById("result-panel");
const errorBanner = document.getElementById("error-banner");

const resultTopic = document.getElementById("result-topic");
const reportContent = document.getElementById("report-content");
const criticContent = document.getElementById("critic-content");
const cacheBadge = document.getElementById("cache-badge");
const downloadBtn = document.getElementById("download-btn");

let currentReport = null;
let currentTopic = "";

// ---------------- Example chips ----------------
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    topicInput.value = chip.dataset.topic;
    topicInput.focus();
  });
});

// ---------------- Voice Input (Web Speech API) ----------------
const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (SpeechRecognitionAPI && micBtn) {
  recognition = new SpeechRecognitionAPI();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  micBtn.addEventListener("click", () => {
    if (isListening) {
      recognition.stop();
      return;
    }
    try {
      recognition.start();
    } catch (err) {
      // recognition might already be running; ignore
    }
  });

  recognition.addEventListener("start", () => {
    isListening = true;
    micBtn.classList.add("listening");
    micBtn.title = "Listening... click to stop";
  });

  recognition.addEventListener("end", () => {
    isListening = false;
    micBtn.classList.remove("listening");
    micBtn.title = "Speak your topic";
  });

  recognition.addEventListener("result", (event) => {
    const transcript = event.results[0][0].transcript;
    topicInput.value = transcript;
    topicInput.focus();
  });

  recognition.addEventListener("error", (event) => {
    isListening = false;
    micBtn.classList.remove("listening");
    micBtn.title = "Speak your topic";

    let message = "Voice input failed. Please try typing instead.";
    if (event.error === "not-allowed" || event.error === "permission-denied") {
      message = "Microphone access denied. Please allow mic permission and try again.";
    } else if (event.error === "no-speech") {
      message = "No speech detected. Please try again.";
    }
    showError(message);
  });
} else if (micBtn) {
  micBtn.style.display = "none";
}

// ---------------- Step status animation ----------------
const STEP_ORDER = ["search", "read", "write", "critic"];
let stepTimer = null;

function resetSteps() {
  STEP_ORDER.forEach((step) => setStepStatus(step, "waiting"));
}

function setStepStatus(step, status) {
  const card = document.querySelector(`.step-card[data-step="${step}"]`);
  if (!card) return;

  card.classList.remove("running", "done");
  const statusEl = card.querySelector(".step-status");

  if (status === "running") {
    card.classList.add("running");
    statusEl.textContent = "● RUNNING";
  } else if (status === "done") {
    card.classList.add("done");
    statusEl.textContent = "✓ DONE";
  } else {
    statusEl.textContent = "WAITING";
  }
}

function startStepAnimation() {
  resetSteps();
  let index = 0;
  setStepStatus(STEP_ORDER[0], "running");

  stepTimer = setInterval(() => {
    setStepStatus(STEP_ORDER[index], "done");
    index++;
    if (index < STEP_ORDER.length) {
      setStepStatus(STEP_ORDER[index], "running");
    } else {
      clearInterval(stepTimer);
    }
  }, 3500);
}

function stopStepAnimation() {
  clearInterval(stepTimer);
  STEP_ORDER.forEach((step) => setStepStatus(step, "done"));
}

// ---------------- Helpers ----------------
function showError(message) {
  errorBanner.textContent = message;
  errorBanner.classList.remove("hidden");
  setTimeout(() => errorBanner.classList.add("hidden"), 5000);
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.querySelector(".btn-label").textContent = isLoading
    ? "Working..."
    : "Run Research Pipeline";
}

// ---------------- Main submit handler ----------------
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const topic = topicInput.value.trim();
  const template = templateSelect ? templateSelect.value : "academic";
  if (!topic) return;

  currentTopic = topic;
  resultPanel.classList.add("hidden");
  setLoading(true);
  startStepAnimation();

  try {
    const response = await fetch(`${API_BASE}/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: topic,
        use_cache: useCacheCheckbox.checked,
        template: template,
      }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || "Something went wrong on the server.");
    }

    const data = await response.json();
    currentReport = data;

    stopStepAnimation();
    setTimeout(() => renderResult(data), 400);

  } catch (err) {
    clearInterval(stepTimer);
    resetSteps();
    showError(err.message || "Could not reach the server. Is the backend running?");
  } finally {
    setLoading(false);
  }
});

// ---------------- Render result ----------------
function renderResult(data) {
  resultPanel.classList.remove("hidden");

  resultTopic.textContent = data.topic || currentTopic;
  reportContent.innerHTML = renderMarkdown(data.report || "No report generated.");

  const score = extractScore(data.feedback);
  const scoreHTML = score !== null
    ? `<div class="score-display"><span class="score-number">${score}</span><span class="score-max">/ 10</span></div>`
    : "";

  criticContent.innerHTML = scoreHTML + renderMarkdown(data.feedback || "No feedback available.");

  if (data.from_cache) {
    cacheBadge.classList.remove("hidden");
  } else {
    cacheBadge.classList.add("hidden");
  }

  resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------------- Download as .md ----------------
downloadBtn.addEventListener("click", () => {
  if (!currentReport) return;

  const blob = new Blob([currentReport.report || ""], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${(currentReport.topic || currentTopic).replace(/\s+/g, "_")}_report.md`;
  a.click();
  URL.revokeObjectURL(url);
});