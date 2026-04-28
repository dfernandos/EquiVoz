from unittest.mock import patch


def register_and_token(client, email="user@test.com", password="secret12", name="Test"):
    """Cria utilizador, simula o link de e-mail, confirma a conta e devolve o token JWT."""
    cap = {"raw": None}

    def _capturar(_dest, _nome, t):
        cap["raw"] = t

    with patch("app.routers.auth.enviar_email_verificacao", side_effect=_capturar):
        r = client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "name": name},
        )
        assert r.status_code == 201, r.get_json()
        assert cap["raw"] is not None
    v = client.get(f"/api/auth/verificar-email?token={cap['raw']}")
    assert v.status_code == 200, v.get_json()
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["access_token"]
