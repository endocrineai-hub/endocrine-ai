#!/usr/bin/env python3
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "ml" / "data" / "processed" / "unified_endocrine_dataset.csv"
ARTIFACTS = ROOT / "ml" / "artifacts"
METRICS_PATH = ARTIFACTS / "metrics.json"

TARGETS = {
    "thyroid": "target_thyroid_risk",
    "diabetes": "target_diabetes_risk",
    "pcos": "target_pcos_risk",
    "adrenal": "target_adrenal_risk",
    "metabolic": "target_metabolic_risk",
}

FEATURES = [
    "age",
    "gender",
    "bmi",
    "sleep_quality",
    "stress_level",
    "exercise_frequency",
    "diet_type",
    "family_history",
    "symptoms",
    "tsh",
    "t3",
    "t4",
    "hba1c",
    "insulin",
    "cortisol",
    "cholesterol",
    "fasting_glucose",
]

NUMERIC = ["age", "bmi", "tsh", "t3", "t4", "hba1c", "insulin", "cortisol", "cholesterol", "fasting_glucose"]
CATEGORICAL = ["gender", "sleep_quality", "stress_level", "exercise_frequency", "diet_type", "family_history", "symptoms"]



def make_preprocessor() -> ColumnTransformer:
    num_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        [
            ("num", num_pipe, NUMERIC),
            ("cat", cat_pipe, CATEGORICAL),
        ]
    )


def model_bank() -> dict:
    return {
        "logistic_regression": LogisticRegression(max_iter=1200),
        "random_forest": RandomForestClassifier(n_estimators=220, random_state=42),
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
        "svm": SVC(probability=True, random_state=42),
    }


def evaluate(y_true, y_pred) -> dict:
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
    }


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    missing = [c for c in FEATURES + list(TARGETS.values()) if c not in df.columns]
    if missing:
        raise SystemExit("Missing required columns: " + ", ".join(missing))

    X = df[FEATURES]
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    all_metrics = {}
    for name, target_col in TARGETS.items():
        y = pd.to_numeric(df[target_col], errors="coerce").fillna(0).astype(int)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
        )

        best_model = None
        best_score = -1
        target_metrics = {}

        for model_name, clf in model_bank().items():
            pipe = Pipeline(
                [
                    ("pre", make_preprocessor()),
                    ("clf", clf),
                ]
            )
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            m = evaluate(y_test, preds)
            target_metrics[model_name] = m

            if m["f1"] > best_score:
                best_score = m["f1"]
                best_model = (model_name, pipe, m)

        assert best_model is not None
        best_name, best_pipe, best_m = best_model
        model_path = ARTIFACTS / f"{name}_best_model.pkl"
        joblib.dump(best_pipe, model_path)
        target_metrics["best"] = {"model": best_name, **best_m, "artifact": str(model_path)}
        all_metrics[name] = target_metrics

        print(f"[{name}] best={best_name} f1={best_m['f1']} saved={model_path.name}")

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"Saved metrics: {METRICS_PATH}")


if __name__ == "__main__":
    main()
