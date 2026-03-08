from backend.services.risk_engine import extract_markers


def test_marker_extraction_tsh_hba1c():
    text = 'TSH: 5.2 HbA1c: 6.0'
    markers = extract_markers(text)
    assert markers['TSH'] == 5.2
    assert markers['HbA1c'] == 6.0
