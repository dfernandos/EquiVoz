from unittest.mock import patch


def test_register_creates_user(client):
    with patch("app.routers.auth.enviar_email_verificacao") as m:
        r = client.post(
            "/api/auth/register",
            json={"email": "novo@test.com", "password": "secret12", "name": "Novo"},
        )
        m.assert_called_once()
    assert r.status_code == 201
    data = r.get_json()
    assert data["email"] == "novo@test.com"
    assert data["name"] == "Novo"
    assert data["id"] == 1
    assert data.get("email_verified") is False
    assert "mensagem" in data


def test_register_rejects_duplicate_email(client):
    with patch("app.routers.auth.enviar_email_verificacao"):
        assert (
            client.post(
                "/api/auth/register",
                json={"email": "dup@test.com", "password": "secret12", "name": "A"},
            ).status_code
            == 201
        )
    r = client.post(
        "/api/auth/register",
        json={"email": "dup@test.com", "password": "secret12", "name": "A"},
    )
    assert r.status_code == 400
    assert r.get_json()["detail"] == "E-mail já cadastrado"


def test_register_validation_error(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "invalid", "password": "short", "name": ""},
    )
    assert r.status_code == 422
    assert "detail" in r.get_json()


def test_login_antes_de_verificar_retorna_403(client):
    with patch("app.routers.auth.enviar_email_verificacao"):
        client.post(
            "/api/auth/register",
            json={"email": "nverif@test.com", "password": "secret12", "name": "N"},
        )
    r = client.post(
        "/api/auth/login",
        json={"email": "nverif@test.com", "password": "secret12"},
    )
    assert r.status_code == 403


def test_verificar_email_e_depois_login_funciona(client):
    raw: dict = {}

    def cap(_dest, _nome, t):
        raw["t"] = t

    with patch("app.routers.auth.enviar_email_verificacao", side_effect=cap):
        r = client.post(
            "/api/auth/register",
            json={"email": "login@test.com", "password": "secret12", "name": "L"},
        )
    assert r.status_code == 201
    assert raw.get("t")
    v = client.get(f"/api/auth/verificar-email?token={raw['t']}")
    assert v.status_code == 200
    r = client.post(
        "/api/auth/login",
        json={"email": "login@test.com", "password": "secret12"},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


def test_me_requires_auth(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_returns_user(client):
    raw: dict = {}

    def cap(_d, _n, t):
        raw["t"] = t

    with patch("app.routers.auth.enviar_email_verificacao", side_effect=cap):
        client.post(
            "/api/auth/register",
            json={"email": "me@test.com", "password": "secret12", "name": "Eu"},
        )
    assert client.get(f"/api/auth/verificar-email?token={raw['t']}").status_code == 200
    r = client.post(
        "/api/auth/login",
        json={"email": "me@test.com", "password": "secret12"},
    )
    token = r.get_json()["access_token"]
    r2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    d = r2.get_json()
    assert d["email"] == "me@test.com"
    assert d["name"] == "Eu"
    assert "id" in d
    assert d.get("email_verified") is True


def test_login_rejects_wrong_password(client):
    raw: dict = {}

    def cap(_d, _n, t):
        raw["t"] = t

    with patch("app.routers.auth.enviar_email_verificacao", side_effect=cap):
        assert (
            client.post(
                "/api/auth/register",
                json={"email": "x@test.com", "password": "secret12", "name": "X"},
            ).status_code
            == 201
        )
    client.get(f"/api/auth/verificar-email?token={raw['t']}")
    r = client.post(
        "/api/auth/login",
        json={"email": "x@test.com", "password": "wrong-password"},
    )
    assert r.status_code == 401
    assert r.get_json()["detail"] == "E-mail ou senha incorretos"


def test_reenviar_verificacao_resposta_generica(client):
    r = client.post(
        "/api/auth/reenviar-verificacao",
        json={"email": "inexistente@nada.com"},
    )
    assert r.status_code == 200
    d = r.get_json()
    assert "detail" in d
    assert "e-mail" in d["detail"].lower() or "envi" in d["detail"].lower()
