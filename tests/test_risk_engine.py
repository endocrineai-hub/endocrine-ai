from backend.services.risk_engine import calculate_risk


def test_calculate_risk_shape():
    profile = {
        'Age': 30,
        'Gender': 'Female',
        'BMI': 27,
        'Sleep quality': 'Poor',
        'Stress level': 'High',
        'Exercise frequency': 'Low',
        'Diet type': 'High sugar',
        'Family history': 'Diabetes',
        'Symptoms': ['Fatigue'],
    }
    out = calculate_risk(profile, {})
    assert 'risk_scores' in out
    assert 'risk_level' in out
