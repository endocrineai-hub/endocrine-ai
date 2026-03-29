# AI-Driven Endocrine Risk Analysis

EndocrineAI is a full-stack preventive healthcare platform for early endocrine and metabolic risk screening.
It combines clinical lifestyle logic, optional ML inference, lab-marker extraction, AI summaries, user portal workflows, and an admin command center.

## 1) What This Product Does

- Predicts early risk trends for:
  - Thyroid dysfunction
  - Insulin resistance / Type 2 diabetes risk
  - PCOS risk (for female profiles)
  - Adrenal stress risk
  - Metabolic syndrome risk
- Extracts marker values from lab report text (`TSH`, `T3`, `T4`, `HbA1c`, `Insulin`, `Cortisol`, `Cholesterol`, `Fasting glucose`)
- Produces structured JSON output for integration
- Supports user login, assessment history, trends, and exports
- Supports admin analytics, user management, user edit, and exports
- Supports AI summary/chat with OpenAI when key is configured

Important: This is clinical decision support, not a diagnosis system.

## 2) Product Batches (Implementation Phases)

### Batch 1: Core Intake + Auth
- Public website and forms
- User registration/login
- Session handling
- Admin login

### Batch 2: Risk Engine + Marker Parsing
- Rule-based endocrine risk engine
- Lab text parser
- JSON risk schema output

### Batch 3: User & Admin Portals
- User dashboard with dedicated pages:
  - Overview
  - New assessment
  - Risk trends
  - History
- Admin dashboard with dedicated pages:
  - Overview
  - Insights
  - Assessments
  - Users (preview/edit/import)

### Batch 4: AI Layer
- OpenAI-generated assessment summary
- OpenAI-based user Q&A (`/api/chat`)
- Safe fallback summary and fallback chat logic

### Batch 5: ML Training + Inference
- Data preparation pipeline
- Model training scripts
- Model artifacts auto-loaded for risk prediction fallback chain

## 3) End-to-End Flow

1. User submits profile and optional lab text.
2. Backend validates profile fields.
3. Lab parser extracts endocrine markers.
4. Rule engine calculates risk scores + levels + triggers.
5. Optional ML model can override risk score block (`use_ml=true`).
6. Optional OpenAI summary generates concise explanation.
7. Assessment is saved to DB with user linkage (if logged in).
8. User dashboard shows trends/history; admin sees platform analytics.

## 4) Tech Stack

- Backend: Flask
- Frontend: Jinja templates + CSS + JS
- DB:
  - Local: SQLite (`backend/data/app.db`)
  - Production: PostgreSQL (Neon or any managed Postgres)
- AI: OpenAI API (optional)
- ML: scikit-learn + pandas + numpy + joblib
- Server: gunicorn (for deployment)

## 5) Project Structure

```text
backend/
  app.py
  config.py
  routes/
    public_routes.py
    auth_routes.py
    admin_routes.py
    api_routes.py
  models/
    db.py
    user_model.py
    assessment_model.py
    admin_model.py
  services/
    risk_engine.py
    model_inference.py
    openai_service.py
    summary_service.py
    chat_service.py
  templates/
  static/
ml/
  data/
  training/
  artifacts/
scripts/
tests/
run.py
api/index.py
render.yaml
vercel.json
```

## 6) API Reference

Base URL (local): `http://127.0.0.1:5000`

### 6.1 POST `/api/assess`
Creates endocrine risk analysis from profile + optional labs.

Request body:
```json
{
  "patient_name": "Ravikant",
  "profile": {
    "Age": 26,
    "Gender": "Male",
    "BMI": 29.6,
    "Sleep quality": "Average",
    "Stress level": "Moderate",
    "Exercise frequency": "Low",
    "Diet type": "High sugar",
    "Family history": "Diabetes",
    "Symptoms": ["Migraine", "Skin itching"]
  },
  "lab_report_text": "TSH: 3.1, HbA1c: 5.9, Fasting Glucose: 108",
  "use_ml": true
}
```

Success response (shape):
```json
{
  "status": "success",
  "extracted_markers": {
    "tsh": 3.1,
    "hba1c": 5.9,
    "fasting_glucose": 108
  },
  "assessment": {
    "risk_scores": {
      "thyroid": "20%",
      "diabetes": "64%",
      "pcos": "0%",
      "adrenal": "35%",
      "metabolic": "58%"
    },
    "risk_level": {
      "thyroid": "Low",
      "diabetes": "Moderate",
      "pcos": "Low",
      "adrenal": "Moderate",
      "metabolic": "Moderate"
    },
    "key_triggers": [],
    "explanation": "...",
    "recommended_actions": [],
    "suggested_tests": [],
    "prediction_source": "ml_model",
    "ai_summary": "...",
    "ai_enabled": true
  }
}
```

### 6.2 POST `/api/extract-markers`
Extracts medical markers from raw lab text.

Request:
```json
{
  "lab_report_text": "TSH: 4.8, T3: 1.2, T4: 8.6, HbA1c: 6.1"
}
```

Response:
```json
{
  "status": "success",
  "extracted_markers": {
    "tsh": 4.8,
    "t3": 1.2,
    "t4": 8.6,
    "hba1c": 6.1
  }
}
```

### 6.3 POST `/api/chat`
Chat-based clarification using assessment context.

Request:
```json
{
  "message": "What should I do first?",
  "assessment": {
    "risk_scores": {
      "diabetes": "72%",
      "metabolic": "69%"
    }
  }
}
```

Response:
```json
{
  "status": "success",
  "reply": "...",
  "disclaimer": "This is preventive risk guidance, not a medical diagnosis."
}
```

### 6.4 GET `/api/model-status`
Returns model and OpenAI availability.

### 6.5 GET `/api/health`
Service health check.

### 6.6 GET `/api/admin/assessments`
Admin-session protected assessments listing.

## 7) Local Setup (macOS)

Prerequisites:
- Python 3.11+
- pip

```bash
cd "/Users/ravikantupadhyay/Documents/GitHub/AI-Driven Endocrine Risk Analysis"
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Set environment variables:
```bash
export SECRET_KEY="change-me"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="admin123"
# Optional
export OPENAI_API_KEY="your_openai_key"
export OPENAI_MODEL="gpt-4o-mini"
# Optional (production-like local DB)
# export DATABASE_URL="postgresql://..."
```

Run:
```bash
python run.py
```

Open:
- Public site: `http://127.0.0.1:5000`
- User login: `http://127.0.0.1:5000/login`
- Admin login: `http://127.0.0.1:5000/admin/login`

## 8) Local Setup (Windows PowerShell)

Prerequisites:
- Python 3.11+ (installed and in PATH)

```powershell
cd "C:\path\to\AI-Driven Endocrine Risk Analysis"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Set env vars:
```powershell
$env:SECRET_KEY="change-me"
$env:ADMIN_USERNAME="admin"
$env:ADMIN_PASSWORD="admin123"
# Optional
$env:OPENAI_API_KEY="your_openai_key"
$env:OPENAI_MODEL="gpt-4o-mini"
# Optional
# $env:DATABASE_URL="postgresql://..."
```

Run:
```powershell
py run.py
```

## 9) Dataset + Model Training

### 9.1 Prepare unified dataset
From CSV:
```bash
python3 scripts/prepare_dataset.py --csv ml/data/raw/local_db_export.csv --source local_db
```

From SQLite table:
```bash
python3 scripts/prepare_dataset.py --sqlite /absolute/path/to/your.db --table your_table_name --source local_db
```

Output:
- `ml/data/processed/unified_endocrine_dataset.csv`

### 9.2 Generate demo dataset quickly
```bash
python3 scripts/generate_demo_training_data.py
```

### 9.3 Train and evaluate
```bash
python3 ml/training/train_classical_models.py
python3 ml/training/evaluate_models.py
```

Artifacts:
- `ml/artifacts/*_best_model.pkl`
- `ml/artifacts/metrics.json`

## 10) Deployment Guide

## 10.1 Render (Recommended Full Deployment)

This repository includes a ready `render.yaml`.

Steps:
1. Push repo to GitHub.
2. In Render, create new Web Service from this repo.
3. Render will read `render.yaml`:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
4. Set environment values in Render dashboard:
   - `SECRET_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `DATABASE_URL` (recommended for persistent production data)
   - `OPENAI_API_KEY` (optional)
   - `OPENAI_MODEL` (optional)
5. Deploy.

Note: if `DATABASE_URL` is missing, app uses local SQLite. For production use Postgres.

## 10.2 Vercel Deployment

Current `vercel.json` deploys Python entrypoint `api/index.py`.

Important:
- Vercel serverless filesystem is ephemeral for local DB writes.
- For stable production data on Vercel, set `DATABASE_URL` to hosted Postgres.

Steps:
1. Import repo in Vercel.
2. Keep framework as "Other" (Vercel Python runtime from `vercel.json`).
3. Add Environment Variables:
   - `SECRET_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `DATABASE_URL` (strongly recommended)
   - `OPENAI_API_KEY` (optional)
   - `OPENAI_MODEL` (optional)
4. Deploy.

## 10.3 Render + Vercel Split (Optional Advanced)

Recommended only if you split frontend and backend repos/apps:
- Render: backend API + DB
- Vercel: frontend-only app

## 11) Admin Notes

Default admin is auto-created from env values on startup.

User management page supports:
- User preview
- Edit name/email/password
- Import users from patient records (for orphan assessments)

## 12) Testing

```bash
python3 -m pytest -q
```

## 13) Troubleshooting

### Admin users show `0`
- Ensure you registered users from `/signup`, or
- In Admin -> Users, click `Import Users From Patient Records`.
- If on Vercel without `DATABASE_URL`, data may reset between invocations.

### AI summary/chat not working
- Ensure `OPENAI_API_KEY` is set.
- Check `/api/model-status` for `openai_available`.

### Model not used
- Ensure model artifacts exist in `ml/artifacts/`.
- Send `"use_ml": true` in `/api/assess` payload.

## 14) Security Checklist

- Change default admin password in production.
- Keep `SECRET_KEY` private and strong.
- Never commit API keys.
- Prefer managed Postgres over SQLite for production.

## 15) License / Academic Usage

This repository is suitable for college project demonstrations and can be extended into a production architecture with stronger auth, RBAC, audit logging, and compliance controls.
