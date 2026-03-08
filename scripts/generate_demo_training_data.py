#!/usr/bin/env python3
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.risk_engine import calculate_risk

OUT = ROOT / "ml" / "data" / "processed" / "unified_endocrine_dataset.csv"


def random_profile(i: int) -> dict:
    gender = random.choice(["Female", "Male"])
    return {
        "Age": random.randint(18, 65),
        "Gender": gender,
        "BMI": round(random.uniform(18, 37), 1),
        "Sleep quality": random.choice(["Poor", "Average", "Good"]),
        "Stress level": random.choice(["High", "Moderate", "Low"]),
        "Exercise frequency": random.choice(["Low", "3 days/week", "Regular", "Daily"]),
        "Diet type": random.choice(["Balanced", "High sugar", "Processed", "High protein"]),
        "Family history": random.choice(["", "Diabetes", "Thyroid", "PCOS", "Diabetes Thyroid"]),
        "Symptoms": random.sample(
            ["Fatigue", "Weight gain", "Sugar cravings", "Irregular cycles", "Acne", "Hair loss"],
            k=random.randint(0, 3),
        ),
    }


def random_markers() -> dict:
    return {
        "TSH": round(random.uniform(0.2, 7.0), 2),
        "T3": round(random.uniform(1.5, 4.5), 2),
        "T4": round(random.uniform(0.5, 1.7), 2),
        "HbA1c": round(random.uniform(4.8, 7.4), 2),
        "Insulin": round(random.uniform(4, 28), 2),
        "Cortisol": round(random.uniform(3, 26), 2),
        "Cholesterol": round(random.uniform(130, 290), 2),
        "Fasting glucose": round(random.uniform(70, 165), 2),
    }


def pct_to_level(v: str) -> int:
    n = int(str(v).replace("%", ""))
    return 1 if n >= 65 else 0


def main() -> None:
    random.seed(42)
    rows = []
    for i in range(1200):
        p = random_profile(i)
        m = random_markers()
        out = calculate_risk(p, m)

        rows.append(
            {
                "age": p["Age"],
                "gender": p["Gender"],
                "bmi": p["BMI"],
                "sleep_quality": p["Sleep quality"],
                "stress_level": p["Stress level"],
                "exercise_frequency": p["Exercise frequency"],
                "diet_type": p["Diet type"],
                "family_history": p["Family history"],
                "symptoms": ", ".join(p["Symptoms"]),
                "tsh": m["TSH"],
                "t3": m["T3"],
                "t4": m["T4"],
                "hba1c": m["HbA1c"],
                "insulin": m["Insulin"],
                "cortisol": m["Cortisol"],
                "cholesterol": m["Cholesterol"],
                "fasting_glucose": m["Fasting glucose"],
                "target_thyroid_risk": pct_to_level(out["risk_scores"]["thyroid"]),
                "target_diabetes_risk": pct_to_level(out["risk_scores"]["diabetes"]),
                "target_pcos_risk": pct_to_level(out["risk_scores"]["pcos"]),
                "target_adrenal_risk": pct_to_level(out["risk_scores"]["adrenal"]),
                "target_metabolic_risk": pct_to_level(out["risk_scores"]["metabolic"]),
                "source": "demo_generated",
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Saved demo dataset: {OUT}")


if __name__ == "__main__":
    main()
