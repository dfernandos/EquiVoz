def test_register_creates_user(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "novo@test.com", "password": "secret12", "name": "Novo"},
    )
    assert r.status_code == 201
    data = r.get_json()
    assert data["email"] == "novo@test.com"
    assert data["name"] == "Novo"
    assert data["id"] == 1
    assert data.get("email_verified") is True
    assert "mensagem" in data


def test_register_rejects_duplicate_email(client):
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


def test_login_apos_registo_funciona(client):
    assert (
        client.post(
            "/api/auth/register",
            json={"email": "log@test.com", "password": "secret12", "name": "L"},
        ).status_code
        == 201
    )
    r = client.post(
        "/api/auth/login",
        json={"email": "log@test.com", "password": "secret12"},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


def test_me_requires_auth(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_returns_user(client):
    client.post(
        "/api/auth/register",
        json={"email": "me@test.com", "password": "secret12", "name": "Eu"},
    )
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
    assert (
        client.post(
            "/api/auth/register",
            json={"email": "x@test.com", "password": "secret12", "name": "X"},
        ).status_code
        == 201
    )
    r = client.post(
        "/api/auth/login",
        json={"email": "x@test.com", "password": "wrong-password"},
    )
    assert r.status_code == 401
    assert r.get_json()["detail"] == "E-mail ou senha incorretos"
