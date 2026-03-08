#!/usr/bin/env python3
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "ml" / "config" / "dataset_schema.json"
OUT_PATH = ROOT / "ml" / "data" / "processed" / "unified_endocrine_dataset.csv"

# Canonical mapping hints for common source column names.
COLUMN_ALIASES = {
    "age": ["age", "patient_age"],
    "gender": ["gender", "sex"],
    "bmi": ["bmi", "body_mass_index"],
    "sleep_quality": ["sleep_quality", "sleep", "sleep_score"],
    "stress_level": ["stress_level", "stress", "stress_score"],
    "exercise_frequency": ["exercise_frequency", "exercise", "activity_level"],
    "diet_type": ["diet_type", "diet", "nutrition_type"],
    "family_history": ["family_history", "family_history_text"],
    "symptoms": ["symptoms", "symptom_text"],
    "tsh": ["tsh"],
    "t3": ["t3", "free_t3"],
    "t4": ["t4", "free_t4"],
    "hba1c": ["hba1c", "a1c"],
    "insulin": ["insulin", "fasting_insulin"],
    "cortisol": ["cortisol"],
    "cholesterol": ["cholesterol", "total_cholesterol"],
    "fasting_glucose": ["fasting_glucose", "glucose_fasting", "glucose"],
    "target_thyroid_risk": ["target_thyroid_risk", "thyroid_label"],
    "target_diabetes_risk": ["target_diabetes_risk", "diabetes_label"],
    "target_pcos_risk": ["target_pcos_risk", "pcos_label"],
    "target_adrenal_risk": ["target_adrenal_risk", "adrenal_label"],
    "target_metabolic_risk": ["target_metabolic_risk", "metabolic_label"],
    "patient_id": ["patient_id", "id"],
    "timestamp": ["timestamp", "created_at", "date"],
    "source": ["source"],
    "notes": ["notes"],
}


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def read_input(csv_path: str | None, sqlite_path: str | None, table: str | None) -> pd.DataFrame:
    if csv_path:
        return pd.read_csv(csv_path)

    if sqlite_path and table:
        conn = sqlite3.connect(sqlite_path)
        try:
            return pd.read_sql_query(f"SELECT * FROM {table}", conn)
        finally:
            conn.close()

    raise ValueError("Provide either --csv or (--sqlite and --table)")


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = {c.lower().strip(): c for c in df.columns}
    out = pd.DataFrame()

    for target, aliases in COLUMN_ALIASES.items():
        picked = None
        for candidate in aliases:
            key = candidate.lower().strip()
            if key in normalized:
                picked = normalized[key]
                break
        out[target] = df[picked] if picked else None

    if out["patient_id"].isna().all():
        # Create pseudo IDs if missing.
        out["patient_id"] = [
            hashlib.sha1(f"row-{i}".encode("utf-8")).hexdigest()[:12] for i in range(len(out))
        ]

    if out["source"].isna().all():
        out["source"] = "local"

    return out


def clean_types(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "age",
        "bmi",
        "tsh",
        "t3",
        "t4",
        "hba1c",
        "insulin",
        "cortisol",
        "cholesterol",
        "fasting_glucose",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    text_cols = [
        "gender",
        "sleep_quality",
        "stress_level",
        "exercise_frequency",
        "diet_type",
        "family_history",
        "symptoms",
        "source",
        "notes",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # Basic imputation.
    for col in ["age", "bmi", "hba1c", "fasting_glucose"]:
        if df[col].notna().any():
            df[col] = df[col].fillna(df[col].median())

    return df


def validate_columns(df: pd.DataFrame, schema: dict) -> list[str]:
    missing = [c for c in schema["required_columns"] if c not in df.columns]
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare unified endocrine dataset")
    parser.add_argument("--csv", help="Input CSV file path")
    parser.add_argument("--sqlite", help="Input SQLite DB path")
    parser.add_argument("--table", help="Table name if using SQLite")
    parser.add_argument("--source", default="local", help="Source name tag")
    args = parser.parse_args()

    raw_df = read_input(args.csv, args.sqlite, args.table)
    df = map_columns(raw_df)
    df["source"] = args.source
    df = clean_types(df)

    schema = load_schema()
    missing = validate_columns(df, schema)
    if missing:
        print("Missing schema columns:", ", ".join(missing))
        raise SystemExit(1)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Saved: {OUT_PATH}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()
