const form = document.getElementById("assessment-form");
const resultSection = document.getElementById("result-section");

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
  };

  const res = await fetch("/api/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    alert("Failed to run analysis");
    return;
  }

  const data = await res.json();
  const out = data.assessment;
  renderRiskCards(out.risk_scores, out.risk_level);
  toListItems("key-triggers", out.key_triggers);
  toListItems("actions", out.recommended_actions);
  toListItems("tests", out.suggested_tests);
  document.getElementById("explanation").textContent = out.explanation;
  document.getElementById("markers-json").textContent = JSON.stringify(data.extracted_markers, null, 2);
  resultSection.classList.remove("hidden");
});
