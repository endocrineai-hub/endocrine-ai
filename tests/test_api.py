from backend.app import create_app


def test_home_route():
    app = create_app()
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200


def test_assess_validation_error():
    app = create_app()
    client = app.test_client()
    resp = client.post('/api/assess', json={'profile': {'Age': 21}})
    assert resp.status_code == 400
    assert resp.get_json()['status'] == 'error'
