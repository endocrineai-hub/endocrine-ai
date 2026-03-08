# Architecture

## Layers
- Frontend: HTML/CSS/JS patient portal + chat UI
- Backend: Flask routes/services/models
- Data: SQLite assessment storage + ML dataset folders
- Model: rule-based engine now, ML pipeline planned in `ml/training/`

## Request Flow
1. User submits profile/lab text.
2. `/api/assess` validates input and extracts markers.
3. Risk engine computes scores.
4. Result stored in DB and returned to UI.
5. Chat endpoint explains report in plain language.
