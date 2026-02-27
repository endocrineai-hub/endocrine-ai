# AI-Driven Endocrine Risk Analysis

This project provides a preventive endocrine risk analysis workflow in three steps:

1. `step-2`: Analyze endocrine health profile data.
2. `step-3`: Extract endocrine markers from lab report text.
3. `step-4`: Compute risk probabilities using extracted markers + lifestyle correlation logic.

## Endocrine Conditions Covered

- Thyroid dysfunction
- Insulin resistance / Type 2 diabetes risk
- PCOS risk (for females)
- Adrenal dysfunction risk
- Metabolic syndrome risk

## JSON Output Format

The analyzer returns:

```json
{
  "risk_scores": {
    "thyroid": "%",
    "diabetes": "%",
    "pcos": "%",
    "adrenal": "%",
    "metabolic": "%"
  },
  "risk_level": {
    "thyroid": "Low / Moderate / High",
    "diabetes": "",
    "pcos": "",
    "adrenal": "",
    "metabolic": ""
  },
  "key_triggers": [],
  "explanation": "",
  "recommended_actions": [],
  "suggested_tests": []
}
```

## Inputs

Profile JSON fields:

- `Age`
- `Gender`
- `BMI`
- `Sleep quality`
- `Stress level`
- `Exercise frequency`
- `Diet type`
- `Family history`
- `Symptoms`
- `Lab results (optional)`

## Run

From project root:

```bash
python3 endocrine_risk_analyzer.py step-2 --profile sample_profile.json
python3 endocrine_risk_analyzer.py step-3 --lab-text sample_lab_report.txt
python3 endocrine_risk_analyzer.py step-4 --profile sample_profile.json
```

Use extracted markers from step-3:

```bash
python3 endocrine_risk_analyzer.py step-3 --lab-text sample_lab_report.txt > markers.json
python3 endocrine_risk_analyzer.py step-4 --profile sample_profile.json --markers-json markers.json
```

## Correlation Logic in Step-4

- Poor sleep + high stress -> adrenal risk increase
- High BMI + diabetes family history -> diabetes risk increase
- Irregular cycles + insulin issues -> PCOS risk increase (female profile)

## GitHub Push

If repository is not initialized:

```bash
git init
git add .
git commit -m "Initial endocrine risk analysis system"
git branch -M main
git remote add origin https://github.com/Ravikant-1811/AI-Driven-Endocrine-Risk-Analysis.git
git push -u origin main
```
