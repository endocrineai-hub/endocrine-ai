from typing import Any, Dict, Iterable


TARGETS = ["thyroid_risk", "diabetes_risk", "pcos_risk", "adrenal_risk", "metabolic_risk"]


def _to_pct(val: Any) -> int:
    try:
        return int(str(val).replace("%", ""))
    except Exception:
        return 0


def build_dashboard_stats(rows: Iterable[dict]) -> Dict[str, Any]:
    rows = list(rows)
    count = len(rows)
    stats = {"total_assessments": count, "avg_scores": {}, "high_risk_counts": {}}

    for key in TARGETS:
        values = [_to_pct(r.get(key)) for r in rows]
        stats["avg_scores"][key] = round(sum(values) / count, 1) if count else 0
        stats["high_risk_counts"][key] = sum(1 for v in values if v >= 65)

    return stats
