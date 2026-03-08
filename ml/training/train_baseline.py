#!/usr/bin/env python3
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "ml" / "data" / "processed" / "unified_endocrine_dataset.csv"
TARGET = "target_diabetes_risk"


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    if TARGET not in df.columns:
        raise SystemExit(f"Missing target column: {TARGET}")

    y = pd.to_numeric(df[TARGET], errors="coerce").fillna(0).astype(int)
    X = df[[c for c in df.columns if c != TARGET]].copy()

    # Dummy setup for baseline F1 only.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = DummyClassifier(strategy="most_frequent")
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print("baseline_f1", round(f1_score(y_test, preds, zero_division=0), 4))


if __name__ == "__main__":
    main()
