# AI-Driven Endocrine Risk Analysis

A complete healthcare web project with:

- Public website for endocrine risk screening
- AI-based endocrine risk engine
- Lab marker extraction from raw report text
- Admin login and dashboard
- Persistent assessment storage (SQLite)
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

- `backend/app.py` Flask server, routes, DB logic
- `backend/risk_engine.py` endocrine scoring and marker extraction
- `backend/templates/` website and admin templates
- `backend/static/` CSS and JS assets
- `backend/data/app.db` SQLite database (auto-created)
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

