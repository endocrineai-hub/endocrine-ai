#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "ml" / "artifacts" / "metrics.json"


def main() -> None:
    if not METRICS.exists():
        raise SystemExit("metrics.json not found. Run train_classical_models.py first")

    with open(METRICS, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Model Evaluation Summary")
    print("=" * 40)
    for target, info in data.items():
        best = info.get("best", {})
        print(
            f"{target:10s} best={best.get('model')} "
            f"acc={best.get('accuracy')} prec={best.get('precision')} rec={best.get('recall')} f1={best.get('f1')}"
        )


if __name__ == "__main__":
    main()
