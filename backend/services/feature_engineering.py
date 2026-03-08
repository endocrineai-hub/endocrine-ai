from typing import Any, Dict


def build_feature_row(profile: Dict[str, Any], markers: Dict[str, Any]) -> Dict[str, Any]:
    symptoms = profile.get("Symptoms", [])
    if isinstance(symptoms, list):
        symptom_text = ", ".join(str(x) for x in symptoms)
    else:
        symptom_text = str(symptoms or "")

    return {
        "age": profile.get("Age"),
        "gender": profile.get("Gender"),
        "bmi": profile.get("BMI"),
        "sleep_quality": profile.get("Sleep quality"),
        "stress_level": profile.get("Stress level"),
        "exercise_frequency": profile.get("Exercise frequency"),
        "diet_type": profile.get("Diet type"),
        "family_history": profile.get("Family history", ""),
        "symptoms": symptom_text,
        "tsh": markers.get("TSH"),
        "t3": markers.get("T3"),
        "t4": markers.get("T4"),
        "hba1c": markers.get("HbA1c"),
        "insulin": markers.get("Insulin"),
        "cortisol": markers.get("Cortisol"),
        "cholesterol": markers.get("Cholesterol"),
        "fasting_glucose": markers.get("Fasting glucose"),
    }
