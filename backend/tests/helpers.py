def register_and_token(client, email="user@test.com", password="secret12", name="Test"):
    """Cria usuário, faz login e devolve o token JWT."""
    r = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    assert r.status_code == 201, r.get_json()
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["access_token"]
