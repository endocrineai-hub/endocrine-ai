#!/usr/bin/env python3
import argparse
import json
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
    if value is None:
        return ""
    return str(value).strip().lower()


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

    # Correlation logic required by step-4.
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

    explanation = (
        "Risk scores were calculated using weighted lifestyle factors, symptom clustering, "
        "family history, and available lab markers, plus correlation logic for adrenal, "
        "diabetes, and PCOS risk pathways."
    )

    recommended_actions = [
        "Improve sleep hygiene (7-8 hours, fixed sleep/wake times).",
        "Adopt moderate-intensity exercise 150+ minutes/week.",
        "Shift to high-fiber, low-processed-sugar diet pattern.",
        "Use stress reduction protocol (breathing, mindfulness, workload control).",
        "Schedule endocrine specialist follow-up if moderate/high risks persist.",
    ]
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
        "explanation": explanation,
        "recommended_actions": recommended_actions,
        "suggested_tests": suggested_tests,
    }


def run_step_2(profile_path: str) -> Dict[str, Any]:
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    labs = profile.get("Lab results (optional)", {}) or {}
    return calculate_risk(profile, labs)


def run_step_3(lab_report_path: str) -> Dict[str, Any]:
    with open(lab_report_path, "r", encoding="utf-8") as f:
        report_text = f.read()
    return {"extracted_markers": extract_markers(report_text)}


def run_step_4(profile_path: str, markers_path: Optional[str]) -> Dict[str, Any]:
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    markers: Dict[str, Optional[float]] = {}
    if markers_path:
        with open(markers_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            markers = raw.get("extracted_markers", raw)
    return calculate_risk(profile, markers)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-Driven Endocrine Risk Analysis System")
    subparsers = parser.add_subparsers(dest="step", required=True)

    step2 = subparsers.add_parser("step-2", help="Analyze endocrine health profile")
    step2.add_argument("--profile", required=True, help="Path to profile JSON")

    step3 = subparsers.add_parser("step-3", help="Extract medical markers from lab text")
    step3.add_argument("--lab-text", required=True, help="Path to lab report text file")

    step4 = subparsers.add_parser("step-4", help="Calculate risk using extracted markers and profile")
    step4.add_argument("--profile", required=True, help="Path to profile JSON")
    step4.add_argument("--markers-json", help="Path to extracted markers JSON")

    args = parser.parse_args()
    if args.step == "step-2":
        result = run_step_2(args.profile)
    elif args.step == "step-3":
        result = run_step_3(args.lab_text)
    else:
        result = run_step_4(args.profile, args.markers_json)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
