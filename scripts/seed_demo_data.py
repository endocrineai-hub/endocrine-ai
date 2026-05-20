import random
from datetime import datetime, timedelta

from backend.app import create_app
from backend.models.assessment_model import save_assessment
from backend.models.db import get_connection

FIRST_NAMES = [
    "Aarav", "Vihaan", "Ananya", "Diya", "Isha", "Riya", "Neha", "Karan", "Aditya", "Meera",
    "Saanvi", "Arjun", "Nikhil", "Pooja", "Rahul", "Sneha", "Yash", "Aditi", "Tanvi", "Kavya",
]
LAST_NAMES = [
    "Sharma", "Gupta", "Verma", "Patel", "Singh", "Kumar", "Mishra", "Jain", "Reddy", "Nair",
]
SYMPTOM_POOL = [
    "Fatigue", "Weight gain", "Hair loss", "Dry skin", "Sugar cravings", "Frequent urination",
    "Increased thirst", "Irregular cycles", "Acne", "Sleep disturbance", "Mood swings",
]
FAMILY_HISTORY_POOL = [
    "None", "Diabetes", "Thyroid", "PCOS", "Diabetes, Thyroid", "Insulin resistance",
]
DIET_POOL = ["Balanced", "High sugar", "Processed/junk", "High carb", "Mediterranean"]
EXERCISE_POOL = ["Low", "2 days/week", "3 days/week", "5 days/week", "Daily"]
SLEEP_POOL = ["Poor", "Average", "Good"]
STRESS_POOL = ["Low", "Moderate", "High"]


def _risk_level(score: int) -> str:
    if score < 35:
        return "Low"
    if score < 65:
        return "Moderate"
    return "High"


def random_profile(gender: str) -> dict:
    age = random.randint(18, 62)
    bmi = round(random.uniform(18.2, 36.8), 1)
    symptoms = random.sample(SYMPTOM_POOL, k=random.randint(2, 4))
    return {
        "Age": age,
        "Gender": gender,
        "BMI": bmi,
        "Sleep quality": random.choice(SLEEP_POOL),
        "Stress level": random.choice(STRESS_POOL),
        "Exercise frequency": random.choice(EXERCISE_POOL),
        "Diet type": random.choice(DIET_POOL),
        "Family history": random.choice(FAMILY_HISTORY_POOL),
        "Symptoms": symptoms,
    }


def random_result(gender: str) -> dict:
    thyroid = random.randint(20, 85)
    diabetes = random.randint(18, 90)
    pcos = random.randint(18, 88) if gender == "Female" else 0
    adrenal = random.randint(22, 86)
    metabolic = random.randint(20, 90)
    risk_scores = {
        "thyroid": f"{thyroid}%",
        "diabetes": f"{diabetes}%",
        "pcos": f"{pcos}%",
        "adrenal": f"{adrenal}%",
        "metabolic": f"{metabolic}%",
    }
    return {
        "risk_scores": risk_scores,
        "risk_level": {k: _risk_level(int(v.replace('%', ''))) for k, v in risk_scores.items()},
        "key_triggers": ["Demo synthetic data"],
        "explanation": "Demo assessment generated for teacher review and dashboard presentation.",
        "recommended_actions": ["Regular exercise", "Sleep optimization", "Endocrinology follow-up"],
        "suggested_tests": ["TSH", "HbA1c", "Fasting glucose", "Lipid profile"],
        "prediction_source": "rule_engine",
        "ai_enabled": False,
        "ai_summary": "Demo summary generated from synthetic sample data.",
    }


def main(seed_count: int = 60) -> None:
    random.seed(42)
    app = create_app()

    with app.app_context():
        for idx in range(seed_count):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            gender = random.choice(["Male", "Female"])
            profile = random_profile(gender)
            result = random_result(gender)
            email = f"{first.lower()}.{last.lower()}{idx}@demo-health.ai"
            mobile = f"9{random.randint(100000000, 999999999)}"

            save_assessment(
                profile=profile,
                result=result,
                patient_name=name,
                patient_email=email,
                patient_mobile=mobile,
            )

        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) AS total FROM assessments").fetchone()
        conn.close()
        total = row["total"] if row and "total" in row.keys() else row[0]

    print(f"Seeded {seed_count} demo assessments successfully.")
    print(f"Total assessments currently in database: {total}")


if __name__ == "__main__":
    main(60)
