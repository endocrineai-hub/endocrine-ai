# AI-Driven Endocrine Risk Analysis

A complete healthcare web project with:

- Public website for endocrine risk screening
- AI-based endocrine risk engine
- Lab marker extraction from raw report text
- Admin login and dashboard
- Persistent assessment storage (SQLite locally, Neon Postgres in production)
- JSON APIs for integration

## Features

### Public Website
- Collects patient profile (age, gender, BMI, stress, sleep, diet, exercise, family history, symptoms)
- Accepts optional lab report text
- Returns structured endocrine risk assessment with:
  - Risk scores (%): thyroid, diabetes, pcos, adrenal, metabolic
  - Risk level: Low/Moderate/High
  - Key triggers
  - Explanation
  - Recommended actions
  - Suggested tests

### Step-3 Lab Marker Extraction
Extracts markers from report text:
- TSH
- T3
- T4
- HbA1c
- Insulin
- Cortisol
- Cholesterol
- Fasting glucose

### Step-4 Correlation Logic
- Poor sleep + high stress -> adrenal risk increase
- High BMI + diabetes family history -> diabetes risk increase
- Irregular cycles + insulin issues -> PCOS risk increase (female)

### Admin Panel
- Login page
- Dashboard with saved assessments and risk outcomes
- Session-based authentication

Default admin credentials (change in production):
- Username: `admin`
- Password: `admin123`

## Project Structure

- `backend/app.py` app factory and blueprint registration
- `backend/config.py` environment-based configuration
- `backend/routes/` modular route groups (`public`, `admin`, `api`)
- `backend/services/` risk and chat services
- `backend/models/` DB initialization and assessment persistence
- `backend/risk_engine.py` core risk logic (shared by service wrapper)
- `backend/templates/` website and admin templates
- `backend/static/` CSS and JS assets
- `backend/data/app.db` SQLite database (auto-created)
- `ml/` model training and evaluation scaffold
- `docs/` architecture/flow/API/report notes
- `tests/` baseline tests for API and risk logic
- `scripts/` utility scripts
- `endocrine_risk_analyzer.py` original CLI analyzer
- `run.py` app entrypoint

## Run Locally

```bash
cd "/Users/ravikantupadhyay/Documents/GitHub/AI-Driven Endocrine Risk Analysis"
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python run.py
```

Open:
- Website: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- Admin login: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

## API Endpoints

### `POST /api/assess`
Request:
```json
{
  "patient_name": "Anita",
  "profile": {
    "Age": 31,
    "Gender": "Female",
    "BMI": 29.2,
    "Sleep quality": "Poor",
    "Stress level": "High",
    "Exercise frequency": "Low",
    "Diet type": "High sugar processed diet",
    "Family history": "Mother: Type 2 Diabetes",
    "Symptoms": ["Irregular cycles", "Fatigue"]
  },
  "lab_report_text": "TSH: 5.2 ..."
}
```

### `POST /api/extract-markers`
Request:
```json
{
  "lab_report_text": "TSH: 5.2, HbA1c: 6.0, Fasting Glucose: 112"
}
```

### `POST /api/chat`
Request:
```json
{
  "message": "What is my highest risk?",
  "assessment": {
    "risk_scores": {
      "thyroid": "60%",
      "diabetes": "72%"
    }
  }
}
```

### `GET /api/model-status`
Returns `model_available` and `openai_available`.

## Tests

```bash
python3 -m pytest tests -q
```

## Dataset Preparation (Your Database + Public Sources)

Use your own database export or table to create a unified training dataset:

```bash
python3 scripts/prepare_dataset.py --csv ml/data/raw/local_db_export.csv --source local_db
```

Or from SQLite directly:

```bash
python3 scripts/prepare_dataset.py --sqlite /absolute/path/to/your.db --table your_table_name --source local_db
```

Output file:
- `ml/data/processed/unified_endocrine_dataset.csv`

Source links are documented in:
- `ml/data/data_sources.md`

### Quick Demo Dataset (for immediate college demo)

```bash
python3 scripts/generate_demo_training_data.py
```

## Train Models (Classical ML)

```bash
python3 ml/training/train_classical_models.py
python3 ml/training/evaluate_models.py
```

This saves:
- `ml/artifacts/*_best_model.pkl`
- `ml/artifacts/metrics.json`

When artifacts exist, `/api/assess` automatically uses ML prediction (`prediction_source: "ml_model"`).  
If artifacts are missing, it falls back to rule engine (`prediction_source: "rule_engine"`).

## OpenAI Integration (AI Summary + AI Chat)

Set your key before running:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"
python3 run.py
```

When enabled:
- `/api/assess` includes `ai_summary`
- `/api/chat` responds with OpenAI-powered answer
- `/api/model-status` shows `openai_available: true`

## Deploy (Neon + Render + Vercel)

### Important: Current App Architecture

This repository is currently a **Flask monolith**:
- Frontend (Jinja templates + static assets)
- Backend APIs
- Auth/admin routes

So if you deploy this repo on both Render and Vercel, each platform is trying to run app code independently.

### Why Vercel asks for env vars again?

Render and Vercel do **not** share secrets.  
Each platform has its own environment-variable store.

Also, because this repo includes `vercel.json` + `api/index.py`, Vercel treats it as a Python backend deployment and asks for backend env vars (`DATABASE_URL`, `SECRET_KEY`, etc.).

### Recommended Option A (Use Render + Neon)

1. Create a Neon project/database.
2. Copy the connection string:
   - `postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require`
3. In Render, deploy this repo using [`render.yaml`](render.yaml).
4. Set env vars in Render:
   - `DATABASE_URL`
   - `ADMIN_PASSWORD`
   - `SECRET_KEY`
   - `OPENAI_API_KEY` (optional)
5. Keep Vercel unused for this repo (or remove `vercel.json` if not needed).

### Option B (Vercel Frontend + Render Backend)

Use this only after splitting the frontend and backend into separate deployable apps.

For split deployment:
1. Deploy backend API on Render (with Neon `DATABASE_URL`).
2. Deploy frontend-only app on Vercel.
3. In Vercel, set only frontend env vars (example: `API_BASE_URL=https://your-render-service.onrender.com`).
4. Do not deploy Flask backend code on Vercel in that setup.

### Notes

- If `DATABASE_URL` is not set, the app uses local SQLite (`backend/data/app.db`).
- With `DATABASE_URL` set to Neon, tables are auto-created at startup.
- For production, always change default admin credentials.

## CLI Steps (Existing)

```bash
python3 endocrine_risk_analyzer.py step-2 --profile sample_profile.json
python3 endocrine_risk_analyzer.py step-3 --lab-text sample_lab_report.txt
python3 endocrine_risk_analyzer.py step-4 --profile sample_profile.json --markers-json markers.json
```

## Push to GitHub

```bash
git add .
git commit -m "Build full endocrine risk web app with admin and APIs"
git push
```
