# AI-Driven Endocrine Risk Analysis: Project Requirements (from Synopsis)

## 1) Core Project Goal
Build an AI-powered **predictive endocrine risk system** that shifts healthcare from reactive diagnosis to proactive risk prediction.

Target disorders:
- Thyroid dysfunction
- Type 2 diabetes / insulin resistance
- PCOS
- Adrenal dysfunction
- Metabolic syndrome

## 2) Problem Statement to Address
Your system must explicitly solve:
- Delayed diagnosis in endocrine care
- Poor handling of hormone time dynamics
- Lack of proactive risk stratification
- Fragmented multi-source healthcare data usage

## 3) Mandatory Objectives
### Data and Processing
- Collect endocrine-relevant data (demographics, lifestyle, symptoms, labs)
- Preprocess: missing values, normalization, outlier handling, feature engineering
- Perform EDA for trends/correlations

### Modeling
- Build predictive models for endocrine risk
- Compare multiple algorithms (baseline + advanced)
- Add temporal modeling for longitudinal signals where available
- Evaluate with accuracy, precision, recall, F1 (classification) and error metrics where needed

### Clinical Utility
- Provide interpretable outputs (risk score + risk level + key triggers)
- Support decision-making, not diagnosis replacement
- Keep architecture scalable for more hormones/disorders

## 4) Gap-Driven System Requirements
Based on your gap analysis, your final submission should include:
1. **Proactive prediction** (future risk tendency, not only current classification)
2. **Temporal intelligence** (at least simple trend/time-window logic now; LSTM/GRU path for expansion)
3. **Deployable product** (web app interface + backend APIs + admin dashboard)
4. **Actionable interpretation** (explanations, suggested tests, recommended actions)

## 5) Functional Modules (for your final project report/demo)
- User profile intake module
- Lab report text parser module
- Risk prediction engine
- Correlation logic module (sleep/stress, BMI/family history, PCOS pattern)
- Explainability module (triggers + recommendations)
- Admin module (login, assessment records, analytics)

## 6) Already Implemented in This Repo
- Web app and form-based risk assessment
- API endpoints for assessment and marker extraction
- Admin login/dashboard
- SQLite persistence for assessments
- Marker extraction: TSH, T3, T4, HbA1c, Insulin, Cortisol, Cholesterol, Fasting glucose
- Structured JSON output with risk scores/levels/triggers/actions/tests

## 7) What You Still Need to Add for Full Academic Alignment
- Proper model training pipeline with dataset versioning
- Multi-model benchmarking report (e.g., Logistic Regression, Random Forest, XGBoost, SVM)
- Temporal model phase (LSTM/GRU) using sequence data
- EDA notebook/visualization outputs
- Evaluation report with confusion matrix and metric comparison tables
- Gantt chart + methodology/block diagram images for final report
- Literature survey references section with citation format

## 8) Suggested Final Architecture for Submission
- Frontend: patient risk website + chat explainer
- Backend: Flask APIs + risk service + feature pipeline
- Data: structured dataset + DB records
- Model Layer:
  - Phase-1: rule + classical ML (deliverable now)
  - Phase-2: deep time-series model (LSTM/GRU)
- Admin: dashboard + export/report support

## 9) Viva/Review-Ready Deliverables Checklist
- Problem statement and gaps mapped to implemented modules
- Dataset description and preprocessing steps
- Model comparison and chosen model justification
- API and UI demonstration
- Admin module demo
- Result interpretation with sample cases
- Limitations and future scope (longitudinal EHR integration)

---
This document is derived directly from `fiy_project akansha.pdf` and mapped to actionable software tasks.
