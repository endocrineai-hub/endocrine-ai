import re
from typing import Any, Dict, List, Optional

MARKER_PATTERNS = {
    "TSH": r"\bTSH\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
    "T3": r"\b(?:T3|Free\s*T3)\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
    "T4": r"\b(?:T4|Free\s*T4)\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
    "HbA1c": r"\b(?:HbA1c|A1c)\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
    "Insulin": r"\bInsulin\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
    "Cortisol": r"\bCortisol\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
    "Cholesterol": r"\b(?:Total\s*)?Cholesterol\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
    "Fasting glucose": r"\b(?:Fasting\s*Glucose|Glucose\s*\(Fasting\))\b\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)",
}


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def pct(value: float) -> str:
    return f"{int(round(clamp(value)))}%"


def risk_level(score: float) -> str:
    if score < 35:
        return "Low"
    if score < 65:
        return "Moderate"
    return "High"


def to_lower_str(value: Any) -> str:
    return "" if value is None else str(value).strip().lower()


def extract_markers(lab_report_text: str) -> Dict[str, Optional[float]]:
    extracted: Dict[str, Optional[float]] = {}
    for marker, pattern in MARKER_PATTERNS.items():
        match = re.search(pattern, lab_report_text, flags=re.IGNORECASE)
        extracted[marker] = float(match.group(1)) if match else None
    return extracted


def calculate_risk(profile: Dict[str, Any], markers: Optional[Dict[str, Optional[float]]] = None) -> Dict[str, Any]:
    markers = markers or {}

    age = float(profile.get("Age", 0) or 0)
    gender = to_lower_str(profile.get("Gender", ""))
    bmi = float(profile.get("BMI", 0) or 0)
    sleep = to_lower_str(profile.get("Sleep quality", "average"))
    stress = to_lower_str(profile.get("Stress level", "moderate"))
    exercise = to_lower_str(profile.get("Exercise frequency", "low"))
    diet = to_lower_str(profile.get("Diet type", "mixed"))
    family_history = to_lower_str(profile.get("Family history", ""))
    symptoms_raw = profile.get("Symptoms", [])
    symptoms: List[str] = [to_lower_str(x) for x in (symptoms_raw if isinstance(symptoms_raw, list) else [symptoms_raw])]

    thyroid = 20.0
    diabetes = 20.0
    pcos = 15.0 if gender == "female" else 0.0
    adrenal = 20.0
    metabolic = 20.0
    key_triggers: List[str] = []

    if bmi >= 30:
        diabetes += 20
        metabolic += 25
        pcos += 10
        key_triggers.append("High BMI")
    elif bmi >= 25:
        diabetes += 12
        metabolic += 15
        pcos += 6
        key_triggers.append("Overweight BMI")

    if "poor" in sleep or "low" in sleep:
        adrenal += 18
        diabetes += 6
        key_triggers.append("Poor sleep")
    elif "average" in sleep:
        adrenal += 8

    if "high" in stress:
        adrenal += 20
        thyroid += 8
        diabetes += 5
        key_triggers.append("High stress")
    elif "moderate" in stress:
        adrenal += 10

    if any(x in exercise for x in ["none", "rare", "sedentary", "low"]):
        diabetes += 12
        metabolic += 12
        key_triggers.append("Low physical activity")
    elif any(x in exercise for x in ["3", "4", "5", "regular", "daily"]):
        diabetes -= 6
        metabolic -= 6

    if any(x in diet for x in ["high sugar", "processed", "junk", "high-carb", "high carb"]):
        diabetes += 14
        metabolic += 10
        pcos += 6
        key_triggers.append("Unhealthy diet pattern")
    elif any(x in diet for x in ["balanced", "mediterranean", "whole foods", "high protein"]):
        diabetes -= 4
        metabolic -= 4

    if any(x in family_history for x in ["diabetes", "insulin resistance"]):
        diabetes += 20
        metabolic += 10
        key_triggers.append("Family history of diabetes")
    if any(x in family_history for x in ["thyroid", "hypothyroid", "hyperthyroid", "hashimoto"]):
        thyroid += 20
        key_triggers.append("Family history of thyroid disorder")
    if "pcos" in family_history and gender == "female":
        pcos += 20
        key_triggers.append("Family history of PCOS")

    symptom_str = " ".join(symptoms)
    if any(x in symptom_str for x in ["fatigue", "weight gain", "cold intolerance", "hair loss", "dry skin"]):
        thyroid += 12
        adrenal += 8
    if any(x in symptom_str for x in ["acanthosis", "increased thirst", "frequent urination", "sugar cravings"]):
        diabetes += 15
    if gender == "female" and any(x in symptom_str for x in ["irregular cycles", "acne", "hirsutism", "ovarian cyst"]):
        pcos += 20
        key_triggers.append("PCOS symptom pattern")

    if age >= 40:
        diabetes += 8
        metabolic += 8

    tsh = markers.get("TSH")
    t3 = markers.get("T3")
    t4 = markers.get("T4")
    hba1c = markers.get("HbA1c")
    insulin = markers.get("Insulin")
    cortisol = markers.get("Cortisol")
    cholesterol = markers.get("Cholesterol")
    fasting_glucose = markers.get("Fasting glucose")

    if tsh is not None and (tsh > 4.5 or tsh < 0.4):
        thyroid += 25
        key_triggers.append("Abnormal TSH")
    if t3 is not None and t3 < 2.0:
        thyroid += 10
    if t4 is not None and t4 < 0.8:
        thyroid += 10
    if hba1c is not None:
        if hba1c >= 6.5:
            diabetes += 35
            metabolic += 20
            key_triggers.append("Diabetic-range HbA1c")
        elif hba1c >= 5.7:
            diabetes += 18
            metabolic += 10
            key_triggers.append("Prediabetic HbA1c")
    if fasting_glucose is not None:
        if fasting_glucose >= 126:
            diabetes += 30
            metabolic += 15
            key_triggers.append("High fasting glucose")
        elif fasting_glucose >= 100:
            diabetes += 15
            metabolic += 8
    if insulin is not None and insulin > 15:
        diabetes += 15
        pcos += 12
        metabolic += 10
        key_triggers.append("Elevated insulin")
    if cortisol is not None and (cortisol > 20 or cortisol < 5):
        adrenal += 20
        key_triggers.append("Abnormal cortisol")
    if cholesterol is not None and cholesterol >= 200:
        metabolic += 15
        key_triggers.append("High cholesterol")

    if ("poor" in sleep or "low" in sleep) and "high" in stress:
        adrenal += 12
        key_triggers.append("Poor sleep + high stress correlation")
    if bmi >= 25 and any(x in family_history for x in ["diabetes", "insulin resistance"]):
        diabetes += 12
        key_triggers.append("High BMI + family history correlation")
    if gender == "female" and "irregular cycles" in symptom_str and (
        (insulin is not None and insulin > 15) or (hba1c is not None and hba1c >= 5.7)
    ):
        pcos += 15
        key_triggers.append("Irregular cycles + insulin issue correlation")

    thyroid = clamp(thyroid)
    diabetes = clamp(diabetes)
    pcos = clamp(pcos)
    adrenal = clamp(adrenal)
    metabolic = clamp(metabolic)

    suggested_tests = [
        "TSH, Free T3, Free T4",
        "HbA1c and fasting glucose",
        "Fasting insulin and HOMA-IR",
        "Morning cortisol",
        "Lipid profile",
    ]
    if gender == "female":
        suggested_tests.append("LH, FSH, Testosterone, pelvic ultrasound (if PCOS suspected)")

    return {
        "risk_scores": {
            "thyroid": pct(thyroid),
            "diabetes": pct(diabetes),
            "pcos": pct(pcos),
            "adrenal": pct(adrenal),
            "metabolic": pct(metabolic),
        },
        "risk_level": {
            "thyroid": risk_level(thyroid),
            "diabetes": risk_level(diabetes),
            "pcos": risk_level(pcos),
            "adrenal": risk_level(adrenal),
            "metabolic": risk_level(metabolic),
        },
        "key_triggers": sorted(set(key_triggers)),
        "explanation": (
            "Risk scores were calculated using weighted lifestyle factors, symptom clustering, "
            "family history, available lab markers, and correlation logic for adrenal, diabetes, and PCOS pathways."
        ),
        "recommended_actions": [
            "Improve sleep hygiene (7-8 hours with fixed timing)",
            "Exercise at least 150 minutes/week",
            "Lower processed sugar and refined carbohydrates",
            "Use daily stress reduction techniques",
            "Review findings with an endocrinologist",
        ],
        "suggested_tests": suggested_tests,
    }
