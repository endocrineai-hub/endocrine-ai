from backend.app import create_app
from backend.models.assessment_model import save_assessment


app = create_app()

with app.app_context():
    profile = {
        "Age": 32,
        "Gender": "Female",
        "BMI": 28.4,
        "Sleep quality": "Poor",
        "Stress level": "High",
        "Exercise frequency": "Low",
        "Diet type": "High sugar",
        "Family history": "Diabetes",
        "Symptoms": ["Fatigue", "Irregular cycles"],
    }
    result = {
        "risk_scores": {
            "thyroid": "62%",
            "diabetes": "72%",
            "pcos": "68%",
            "adrenal": "70%",
            "metabolic": "66%",
        }
    }
    save_assessment(profile, result, "Demo Patient")

print("Seeded demo assessment")
