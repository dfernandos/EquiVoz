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


def test_register_rejects_duplicate_email(client):
    body = {"email": "dup@test.com", "password": "secret12", "name": "A"}
    assert client.post("/api/auth/register", json=body).status_code == 201
    r = client.post("/api/auth/register", json=body)
    assert r.status_code == 400
    assert r.get_json()["detail"] == "E-mail já cadastrado"


def test_register_validation_error(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "invalid", "password": "short", "name": ""},
    )
    assert r.status_code == 422
    assert "detail" in r.get_json()


def test_login_returns_token(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@test.com", "password": "secret12", "name": "L"},
    )
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


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "x@test.com", "password": "secret12", "name": "X"},
    )
    r = client.post(
        "/api/auth/login",
        json={"email": "x@test.com", "password": "wrong-password"},
    )
    assert r.status_code == 401
    assert r.get_json()["detail"] == "E-mail ou senha incorretos"
