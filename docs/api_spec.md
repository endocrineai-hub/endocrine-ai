# API Specification

Base URL (local): `http://127.0.0.1:5000`

## Authentication Model

- User routes (`/dashboard/*`) require user session.
- Admin routes (`/admin/*`, `/api/admin/assessments`) require admin session.
- Sessions are cookie-based (Flask session).

## POST /api/assess

Create endocrine risk analysis from profile + optional lab text.

### Request JSON

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
  "lab_report_text": "TSH: 5.2, HbA1c: 6.1, Fasting Glucose: 112",
  "use_ml": true
}
```

### Validation Rules

- Required profile fields:
  - `Age`, `Gender`, `BMI`, `Sleep quality`, `Stress level`, `Exercise frequency`, `Diet type`
- `Age` must be 1 to 120.
- `BMI` must be 10 to 80.

### Response JSON

```json
{
  "status": "success",
  "extracted_markers": {},
  "assessment": {
    "risk_scores": {},
    "risk_level": {},
    "key_triggers": [],
    "explanation": "",
    "recommended_actions": [],
    "suggested_tests": [],
    "prediction_source": "rule_engine",
    "ai_summary": "",
    "ai_enabled": false
  }
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": ["Missing required field: Age"]
}
```

## POST /api/extract-markers

Extract lab markers from free-text report.

### Request JSON

```json
{
  "lab_report_text": "TSH: 3.8, T3: 1.1, T4: 8.5, HbA1c: 5.9"
}
```

### Response JSON

```json
{
  "status": "success",
  "extracted_markers": {
    "tsh": 3.8,
    "t3": 1.1,
    "t4": 8.5,
    "hba1c": 5.9
  }
}
```

## POST /api/chat

Generate contextual user guidance from current assessment.

### Request JSON

```json
{
  "message": "What should I improve first?",
  "assessment": {
    "risk_scores": {
      "diabetes": "72%",
      "metabolic": "68%"
    }
  }
}
```

### Response JSON

```json
{
  "status": "success",
  "reply": "...",
  "disclaimer": "This is preventive risk guidance, not a medical diagnosis."
}
```

## GET /api/model-status

Returns service readiness:

```json
{
  "status": "success",
  "model_available": true,
  "openai_available": true
}
```

## GET /api/health

Basic health endpoint:

```json
{
  "status": "success",
  "service": "endocrine-risk-platform"
}
```

## GET /api/admin/assessments

Admin-protected endpoint for full assessment list.

### Auth

- Requires valid admin session cookie.

### Response JSON

```json
{
  "assessments": []
}
```
