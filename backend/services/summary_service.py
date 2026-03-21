from typing import Dict, List


def build_fallback_summary(result: Dict, triggers: List[str]) -> str:
    scores = result.get("risk_scores", {})
    levels = result.get("risk_level", {})

    def _pct(val: str) -> int:
        try:
            return int(str(val).replace("%", ""))
        except Exception:
            return 0

    ranked = sorted(scores.items(), key=lambda kv: _pct(kv[1]), reverse=True)
    if not ranked:
        return "No risk summary available."

    top = ranked[:2]
    top_bits = ", ".join([f"{k} {scores.get(k)} ({levels.get(k, 'N/A')})" for k, _ in top])
    trigger_bits = ", ".join(triggers[:4]) if triggers else "No dominant triggers identified"

    return (
        "Summary: Highest risks observed in "
        + top_bits
        + ". Key trigger signals: "
        + trigger_bits
        + ". Follow suggested tests and lifestyle actions for confirmation and prevention."
    )
