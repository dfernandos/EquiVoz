"""Testes unitários: hashing e JWT (sem banco / sem app Flask)."""

import pytest

from app import auth_utils


@pytest.fixture
def jwt_settings(monkeypatch):
    monkeypatch.setattr(auth_utils.settings, "secret_key", "test-secret-key-at-least-32-bytes-long!!")
    monkeypatch.setattr(auth_utils.settings, "algorithm", "HS256")
    monkeypatch.setattr(auth_utils.settings, "access_token_expire_minutes", 60)


def test_hash_and_verify_password_roundtrip():
    raw = "senha-segura-123"
    hashed = auth_utils.hash_password(raw)
    assert hashed != raw
    assert auth_utils.verify_password(raw, hashed)
    assert not auth_utils.verify_password("outra-senha", hashed)


def test_create_and_decode_token(jwt_settings):
    token = auth_utils.create_access_token("user@example.com")
    assert isinstance(token, str) and len(token) > 20
    assert auth_utils.decode_token(token) == "user@example.com"


def test_decode_token_invalid_returns_none(jwt_settings):
    assert auth_utils.decode_token("invalid.jwt.here") is None
