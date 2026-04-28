from tests.helpers import register_and_token


def test_tipos_violacao_list(client):
    r = client.get("/api/denuncias/tipos-violacao")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    ids = {item["id"] for item in data}
    assert "racismo" in ids
    assert all("label" in item for item in data)


def test_create_denuncia_requires_auth(client):
    r = client.post(
        "/api/denuncias",
        json={
            "title": "Título mínimo ok",
            "description": "Descrição com mais de dez caracteres.",
            "violation_type": "racismo",
        },
    )
    assert r.status_code == 401
    assert r.get_json()["detail"] == "Não autenticado"


def test_create_denuncia_success(client):
    token = register_and_token(client)
    r = client.post(
        "/api/denuncias",
        json={
            "title": "Relato de teste",
            "description": "Texto descritivo com pelo menos dez caracteres.",
            "violation_type": "servico_publico",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    data = r.get_json()
    assert data["title"] == "Relato de teste"
    assert data["violation_type"] == "servico_publico"
    assert data["user_id"] == 1
    assert data.get("empresa") is None


def test_estatisticas_dashboard_publico_sem_auth(client):
    r = client.get("/api/denuncias/estatisticas/dashboard")
    assert r.status_code == 200
    d = r.get_json()
    assert "total" in d
    assert "minhas" in d
    assert d["minhas"] == 0


def test_estatisticas_dashboard_formato(client):
    token = register_and_token(client, email="dash@example.com")
    r = client.get(
        "/api/denuncias/estatisticas/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    d = r.get_json()
    assert d["total"] == 0
    assert d["com_localizacao_mapa"] == 0
    assert d["minhas"] == 0
    assert d["por_tipo"] == []
    assert d["por_mes"] == []
    assert d["top_empresas"] == []


def test_estatisticas_dashboard_por_mes_usa_data_ocorrencia(client):
    """Série por mês usa COALESCE(occurred_at, created_at), como a listagem com filtro de datas."""
    from datetime import datetime, timedelta, timezone

    t = register_and_token(client, email="dash.mesocor@example.com")
    occurred = datetime.now(timezone.utc) - timedelta(days=60)
    assert (
        client.post(
            "/api/denuncias",
            json={
                "title": "Relato com ocorrência antiga",
                "description": "Mais de dez caracteres descrição longa aqui.",
                "violation_type": "outro",
                "occurred_at": occurred.replace(microsecond=0).isoformat(),
            },
            headers={"Authorization": f"Bearer {t}"},
        ).status_code
        == 201
    )
    d = client.get(
        "/api/denuncias/estatisticas/dashboard",
        headers={"Authorization": f"Bearer {t}"},
    ).get_json()
    ymo = occurred.strftime("%Y-%m")
    assert any(
        m["mes"] == ymo and m["registros"] == 1 for m in d["por_mes"]
    ), f"esperava mês {ymo} em {d['por_mes']}"


def test_estatisticas_empresas_requires_auth(client):
    r = client.get("/api/denuncias/estatisticas/empresas")
    assert r.status_code == 401


def test_estatisticas_empresas_por_titulo_quando_sem_empresa(client):
    """Rótulo de agrupamento: COALESCE(empresa, título)."""
    t = register_and_token(client, email="sem.emp@example.com")
    r = client.post(
        "/api/denuncias",
        json={
            "title": "Problema no Lugar Exemplo Só Título",
            "description": "Mais de dez caracteres no corpo do relato para validar o fluxo da API.",
            "violation_type": "outro",
        },
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 201
    r2 = client.get(
        "/api/denuncias/estatisticas/empresas?limit=10",
        headers={"Authorization": f"Bearer {t}"},
    )
    data = r2.get_json()
    by_tit = [x for x in data if "Lugar Exemplo" in (x.get("empresa") or "")]
    assert len(by_tit) == 1
    assert by_tit[0]["total"] == 1
    assert by_tit[0]["minhas"] == 1


def test_estatisticas_empresas_total_e_minhas(client):
    t = register_and_token(client, email="e1@example.com")
    assert client.post(
        "/api/denuncias",
        json={
            "title": "Primeiro relato",
            "description": "Mais de dez caracteres no texto.",
            "violation_type": "outro",
            "empresa": "Cafe Central",
        },
        headers={"Authorization": f"Bearer {t}"},
    ).status_code == 201
    t2 = register_and_token(client, email="e2@example.com")
    assert client.post(
        "/api/denuncias",
        json={
            "title": "Segundo relato",
            "description": "Mais de dez caracteres no texto.",
            "violation_type": "outro",
            "empresa": "Cafe Central",
        },
        headers={"Authorization": f"Bearer {t2}"},
    ).status_code == 201
    r = client.get(
        "/api/denuncias/estatisticas/empresas?limit=5",
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert r.status_code == 200
    data = r.get_json()
    cafe = [x for x in data if x["empresa"] == "Cafe Central"]
    assert len(cafe) == 1
    assert cafe[0]["total"] == 2
    assert cafe[0]["minhas"] == 1


def test_lista_todas_denuncias_requires_auth(client):
    r = client.get("/api/denuncias")
    assert r.status_code == 401


def test_lista_filtra_empresa_tipo_e_data(client):
    from datetime import date, datetime, timezone

    token = register_and_token(client, email="filtros@example.com")
    r = client.post(
        "/api/denuncias",
        json={
            "title": "Atendimento Habbibs",
            "description": "Relato com pelo menos dez caracteres no corpo do texto.",
            "violation_type": "racismo",
            "empresa": "Habbibs",
            "occurred_at": datetime(2024, 6, 10, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    d = r.get_json()
    did = d["id"]

    r = client.get(
        "/api/denuncias?empresa=Habbibs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert any(x["id"] == did for x in r.get_json())

    r = client.get(
        "/api/denuncias?violation_type=discriminacao_orientacao",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert not any(x["id"] == did for x in r.get_json())

    r = client.get(
        f"/api/denuncias?data_inicio={date(2024, 6, 1)}&data_fim={date(2024, 6, 30)}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert any(x["id"] == did for x in r.get_json())

    r = client.get(
        f"/api/denuncias?data_inicio={date(2024, 7, 1)}&data_fim={date(2024, 7, 31)}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert not any(x["id"] == did for x in r.get_json())


def test_lista_todas_inclui_denuncia_de_outro_usuario(client):
    token_a = register_and_token(client, email="a@example.com")
    client.post(
        "/api/denuncias",
        json={
            "title": "Visível na lista geral",
            "description": "Mais de dez caracteres para a API aceitar o corpo.",
            "violation_type": "outro",
            "latitude": -15.0,
            "longitude": -47.9,
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )

    token_b = register_and_token(client, email="b@example.com")
    r = client.get("/api/denuncias", headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 200
    rows = r.get_json()
    assert len(rows) >= 1
    found = [x for x in rows if x["title"] == "Visível na lista geral"]
    assert len(found) == 1
    assert found[0]["latitude"] == -15.0
    assert found[0]["longitude"] == -47.9


def test_minhas_denuncias_empty_then_one(client):
    token = register_and_token(client)
    r = client.get("/api/denuncias/minhas", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json() == []

    client.post(
        "/api/denuncias",
        json={
            "title": "Outro relato",
            "description": "Mais de dez caracteres aqui.",
            "violation_type": "outro",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get("/api/denuncias/minhas", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    rows = r.get_json()
    assert len(rows) == 1
    assert rows[0]["violation_type"] == "outro"


def test_get_put_delete_denuncia_somente_autor(client):
    from datetime import datetime, timezone

    t_a = register_and_token(client, email="autor@example.com")
    t_b = register_and_token(client, email="outro@example.com")
    r = client.post(
        "/api/denuncias",
        json={
            "title": "Minha denúncia editável",
            "description": "Texto com mais de dez caracteres.",
            "violation_type": "outro",
            "empresa": "Antiga",
        },
        headers={"Authorization": f"Bearer {t_a}"},
    )
    assert r.status_code == 201
    did = r.get_json()["id"]

    r = client.get(f"/api/denuncias/{did}", headers={"Authorization": f"Bearer {t_b}"})
    assert r.status_code == 403

    r = client.get(f"/api/denuncias/{99999}", headers={"Authorization": f"Bearer {t_a}"})
    assert r.status_code == 404

    r = client.get(f"/api/denuncias/{did}", headers={"Authorization": f"Bearer {t_a}"})
    assert r.status_code == 200
    assert r.get_json()["title"] == "Minha denúncia editável"

    r = client.put(
        f"/api/denuncias/{did}",
        json={
            "title": "Título atualizado",
            "description": "Texto com mais de dez caracteres longo.",
            "violation_type": "racismo",
            "empresa": "Nova",
            "occurred_at": datetime(2025, 3, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat(),
        },
        headers={"Authorization": f"Bearer {t_a}"},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["title"] == "Título atualizado"
    assert data["violation_type"] == "racismo"
    assert data["empresa"] == "Nova"

    r = client.delete(
        f"/api/denuncias/{did}",
        headers={"Authorization": f"Bearer {t_b}"},
    )
    assert r.status_code == 403

    r = client.delete(
        f"/api/denuncias/{did}",
        headers={"Authorization": f"Bearer {t_a}"},
    )
    assert r.status_code == 204
    assert r.data == b""

    r = client.get(f"/api/denuncias/{did}", headers={"Authorization": f"Bearer {t_a}"})
    assert r.status_code == 404
