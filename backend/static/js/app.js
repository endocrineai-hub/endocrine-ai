const form = document.getElementById("assessment-form");
const resultSection = document.getElementById("result-section");
const chatForm = document.getElementById("chat-form");
const chatLog = document.getElementById("chat-log");
const chatInput = document.getElementById("chat-input");
let riskChart = null;
let latestAssessment = null;

function toListItems(targetId, items) {
  const el = document.getElementById(targetId);
  el.innerHTML = "";
  (items || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  });
}

function renderRiskCards(scores, levels) {
  const container = document.getElementById("risk-cards");
  container.innerHTML = "";
  Object.keys(scores).forEach((key) => {
    const card = document.createElement("div");
    card.className = "risk-card";
    card.innerHTML = `
      <h4>${key}</h4>
      <p><strong>${scores[key]}</strong></p>
      <p class="level-${levels[key]}">${levels[key]}</p>
    `;
    container.appendChild(card);
  });
}

function appendChatMessage(text, role) {
  if (!chatLog) return;
  const msg = document.createElement("div");
  msg.className = `chat-message ${role === "user" ? "chat-user" : "chat-ai"}`;
  msg.textContent = text;
  chatLog.appendChild(msg);
  chatLog.scrollTop = chatLog.scrollHeight;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  const profile = {
    "Age": Number(fd.get("age")),
    "Gender": fd.get("gender"),
    "BMI": Number(fd.get("bmi")),
    "Sleep quality": fd.get("sleep_quality"),
    "Stress level": fd.get("stress_level"),
    "Exercise frequency": fd.get("exercise_frequency"),
    "Diet type": fd.get("diet_type"),
    "Family history": fd.get("family_history"),
    "Symptoms": String(fd.get("symptoms") || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
  };

  const payload = {
    patient_name: fd.get("patient_name") || "Anonymous",
    profile,
    lab_report_text: fd.get("lab_report_text") || "",
    use_ml: Boolean(fd.get("use_ml")),
  };

  const res = await fetch("/api/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorPayload = await res.json().catch(() => ({}));
    const validationErrors = (errorPayload.errors || []).join("\n");
    alert(validationErrors || errorPayload.message || "Failed to run analysis");
    return;
  }

  const data = await res.json();
  const out = data.assessment;
  latestAssessment = out;
  if (chatLog) {
    chatLog.innerHTML = "";
  }
  document.getElementById("prediction-source").textContent =
    `Prediction source: ${out.prediction_source || "rule_engine"}`;

  const aiWrap = document.getElementById("ai-summary-wrap");
  const aiSummary = document.getElementById("ai-summary");
  if (out.ai_summary) {
    aiSummary.textContent = out.ai_summary;
    aiWrap.classList.remove("hidden");
  } else {
    aiSummary.textContent = "";
    aiWrap.classList.add("hidden");
  }

  renderRiskCards(out.risk_scores, out.risk_level);
  renderRiskChart(out.risk_scores);
  toListItems("key-triggers", out.key_triggers);
  toListItems("actions", out.recommended_actions);
  toListItems("tests", out.suggested_tests);
  document.getElementById("explanation").textContent = out.explanation;
  document.getElementById("markers-json").textContent = JSON.stringify(data.extracted_markers, null, 2);
  resultSection.classList.remove("hidden");
});

if (chatForm) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = (chatInput?.value || "").trim();
    if (!message) return;
    if (!latestAssessment) {
      appendChatMessage("Run an assessment first so I can answer with context.", "ai");
      return;
    }

    appendChatMessage(message, "user");
    if (chatInput) chatInput.value = "";

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, assessment: latestAssessment }),
      });
      const payload = await res.json();
      if (!res.ok || payload.status !== "success") {
        appendChatMessage(payload.message || "Unable to answer right now.", "ai");
        return;
      }
      appendChatMessage(payload.reply, "ai");
    } catch (err) {
      appendChatMessage("Network error. Try again in a moment.", "ai");
    }
  });
}

function renderRiskChart(scores) {
  const ctx = document.getElementById("risk-chart");
  if (!ctx || !window.Chart) return;
  const labels = Object.keys(scores);
  const values = labels.map((k) => Number(String(scores[k]).replace("%", "")));

  if (riskChart) {
    riskChart.destroy();
  }

  riskChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Risk %",
          data: values,
          backgroundColor: "rgba(11, 107, 113, 0.55)",
          borderColor: "rgba(11, 107, 113, 1)",
          borderWidth: 1,
          borderRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: { beginAtZero: true, max: 100 },
      },
    },
  });
}
