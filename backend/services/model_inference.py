import os
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .feature_engineering import build_feature_row

TARGETS = ["thyroid", "diabetes", "pcos", "adrenal", "metabolic"]
MODEL_DIR = Path(__file__).resolve().parents[2] / "ml" / "artifacts"


def _risk_level(score: int) -> str:
    if score < 35:
        return "Low"
    if score < 65:
        return "Moderate"
    return "High"


def _load_model(path: Path):
    import joblib

    return joblib.load(path)


def model_available() -> bool:
    return all((MODEL_DIR / f"{t}_best_model.pkl").exists() for t in TARGETS)


def predict_with_models(profile: Dict[str, Any], markers: Dict[str, Any]) -> Dict[str, Any] | None:
    if not model_available():
        return None

    row = build_feature_row(profile, markers)
    df = pd.DataFrame([row])

    scores: Dict[str, str] = {}
    levels: Dict[str, str] = {}

    for target in TARGETS:
        model_path = MODEL_DIR / f"{target}_best_model.pkl"
        model = _load_model(model_path)

        if hasattr(model, "predict_proba"):
            proba = float(model.predict_proba(df)[0][1])
            score = int(round(proba * 100))
        else:
            pred = int(model.predict(df)[0])
            score = 75 if pred == 1 else 25

        scores[target] = f"{score}%"
        levels[target] = _risk_level(score)

    return {
        "risk_scores": scores,
        "risk_level": levels,
        "prediction_source": "ml_model",
        "explanation": "Risk scores predicted by trained ML models using profile + lab features.",
    }
