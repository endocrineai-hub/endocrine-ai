# Project Structure and Flow (What to Change, What to Add)

## 1) Current Structure (Now)

```text
AI-Driven Endocrine Risk Analysis/
  backend/
    app.py
    risk_engine.py
    requirements.txt
    templates/
      index.html
      admin_login.html
      admin_dashboard.html
    data/
      app.db
  endocrine_risk_analyzer.py
  run.py
  sample_profile.json
  sample_lab_report.txt
  README.md
  PROJECT_REQUIREMENTS_FROM_SYNOPIS.md
```

## 2) Target Structure (Recommended for Final Project)

```text
AI-Driven Endocrine Risk Analysis/
  backend/
    app.py
    config.py
    requirements.txt
    routes/
      public_routes.py
      admin_routes.py
      api_routes.py
    services/
      risk_engine.py
      chat_service.py
      feature_engineering.py
      report_service.py
    models/
      db.py
      assessment_model.py
    templates/
      index.html
      admin_login.html
      admin_dashboard.html
    static/
      css/styles.css
      js/app.js
    data/
      app.db

  ml/
    data/
      raw/
      processed/
    notebooks/
      01_eda.ipynb
      02_model_training.ipynb
    training/
      train_baseline.py
      train_classical_models.py
      evaluate_models.py
      train_lstm_gru.py
    artifacts/
      best_model.pkl
      scaler.pkl
      metrics.json

  docs/
    architecture.md
    flow.md
    api_spec.md
    report_outline.md
    gantt_chart.png
    block_diagram.png

  tests/
    test_api.py
    test_risk_engine.py
    test_marker_extraction.py

  scripts/
    seed_demo_data.py
    export_assessments.py

  endocrine_risk_analyzer.py
  run.py
  README.md
  .gitignore
```

## 3) Functional Flow (Simple)

1. User fills profile + optional lab text on website.
2. Frontend sends request to `/api/assess`.
3. Backend extracts lab markers.
4. Risk engine computes scores and risk levels.
5. Response returns JSON (scores, triggers, actions, tests).
6. Assessment is saved in SQLite.
7. Admin dashboard shows all historical assessments.
8. Chat API explains report in user-friendly language.

## 4) Data and Model Flow (Academic)

1. Collect dataset (demographic + lifestyle + symptoms + labs + labels).
2. Preprocess (missing values, encoding, scaling, outliers).
3. EDA (correlations, distributions, imbalance checks).
4. Train baseline models (LR, RF, SVM, XGBoost).
5. Evaluate (accuracy, precision, recall, F1, AUC).
6. Temporal phase (LSTM/GRU with sequence windows).
7. Save best model artifacts.
8. Integrate model inference into backend API.

## 5) What to Keep / Modify / Add

### Keep

- Current Flask web app and admin panel
- Current marker extraction logic
- Current JSON response format
- Current database logging of assessments

### Modify

- Split `backend/app.py` into modular routes and services
- Move `risk_engine.py` under `backend/services/`
- Add model-based scoring path (not only rules)
- Add stronger validation and error handling for APIs
- Add role-safe admin auth config via environment variables

### Add

- `ml/` training pipeline and notebooks
- Model artifact loading in production API
- Automated tests (`tests/`)
- Analytics in admin dashboard (risk trend charts)
- Export feature (CSV/PDF report)
- Deployment files (`Dockerfile`, optional `docker-compose.yml`)

## 6) Immediate Step-by-Step Plan

### Phase-1 (Stabilize App)

- Add missing chat UI + `/api/chat` integration in frontend.
- Refactor backend into `routes/` and `services/`.
- Add API input validation.

### Phase-2 (ML Core)

- Prepare dataset schema in `ml/data/`.
- Build EDA notebook.
- Train and compare 3-5 classical models.
- Save metrics and best model.

### Phase-3 (Temporal + Final Submission)

- Add sequence model (LSTM/GRU).
- Add final metrics table and confusion matrix.
- Generate diagrams (flowchart, block diagram, gantt).
- Finalize report mapping implementation to synopsis objectives.

## 7) Change Decision Guide (When you ask "What should I change now?")

If your goal is **demo working product**:

- Focus on UI polish, admin analytics, and API stability.

If your goal is **academic marks + viva**:

- Focus first on `ml/notebooks`, model comparison, evaluation report, temporal model.

If your goal is **deployment-ready project**:

- Focus on modular architecture, tests, Docker, env-based config, logging.

---

Use this file as the master checklist before each coding step.
