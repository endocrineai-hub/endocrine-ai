from backend.models.db import _sanitize_database_url


def test_sanitize_removes_channel_binding_param():
    url = "postgresql://u:p@host/db?sslmode=require&channel_binding=require"
    out = _sanitize_database_url(url)
    assert "channel_binding" not in out
    assert "sslmode=require" in out


def test_sanitize_keeps_other_query_params():
    url = "postgresql://u:p@host/db?sslmode=require&connect_timeout=10"
    out = _sanitize_database_url(url)
    assert "sslmode=require" in out
    assert "connect_timeout=10" in out
