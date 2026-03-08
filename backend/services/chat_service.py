def generate_chat_reply(message: str, assessment: dict) -> str:
    msg = (message or "").strip().lower()
    risk_scores = (assessment or {}).get("risk_scores", {})
    risk_level = (assessment or {}).get("risk_level", {})
    tests = (assessment or {}).get("suggested_tests", [])
    actions = (assessment or {}).get("recommended_actions", [])

    if not msg:
        return "Please ask a question about your endocrine health risk report."

    if any(token in msg for token in ["highest", "most risk", "top risk"]):
        if not risk_scores:
            return "Run an assessment first, then I can explain your highest-risk area."
        numeric = {}
        for key, val in risk_scores.items():
            try:
                numeric[key] = int(str(val).replace("%", ""))
            except ValueError:
                continue
        if not numeric:
            return "I could not read risk percentages from the report. Please run the analysis again."
        top = max(numeric, key=numeric.get)
        return f"Your highest estimated risk is {top} at {numeric[top]}% ({risk_level.get(top, 'N/A')})."

    if any(token in msg for token in ["thyroid", "diabetes", "pcos", "adrenal", "metabolic"]):
        if not risk_scores:
            return "Please run the assessment first so I can explain condition-specific risk."
        for key in ["thyroid", "diabetes", "pcos", "adrenal", "metabolic"]:
            if key in msg:
                return (
                    f"{key.capitalize()} risk is {risk_scores.get(key, 'N/A')} "
                    f"with level {risk_level.get(key, 'N/A')}. "
                    "I can also suggest next tests or lifestyle priorities for this risk."
                )

    if any(token in msg for token in ["test", "lab", "checkup"]):
        if not tests:
            return "No test suggestions are available yet. Run an assessment first."
        return "Suggested tests: " + "; ".join(tests[:6])

    if any(token in msg for token in ["action", "improve", "reduce", "what should i do", "next step"]):
        if not actions:
            return "No recommendations are available yet. Run an assessment first."
        return "Top actions: " + "; ".join(actions[:4])

    if any(token in msg for token in ["can you diagnose", "diagnose", "cure", "medicine", "prescription"]):
        return (
            "I cannot diagnose disease or prescribe medicine. "
            "I provide risk screening guidance only. Please consult a licensed clinician."
        )

    return (
        "I can help explain your risk scores, likely triggers, suggested tests, and priority lifestyle actions. "
        "Try: 'What is my highest risk?' or 'What tests should I do next?'"
    )
