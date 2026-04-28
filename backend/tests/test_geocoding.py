import io
import json
from unittest.mock import patch

from tests.helpers import register_and_token


def test_geocoding_requer_auth(client):
    r = client.get("/api/geocoding/search?q=Porto+Alegre+RS")
    assert r.status_code == 401


def test_geocoding_endereco_curto(client):
    t = register_and_token(client, email="geo1@e.com")
    r = client.get(
        "/api/geocoding/search?q=ab",
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 400


@patch("app.routers.geocoding.urllib.request.urlopen")
def test_geocoding_nominatim_sucesso(mock_urlopen, client):
    t = register_and_token(client, email="geo2@e.com")
    body = json.dumps(
        [
            {
                "lat": "-30.0346",
                "lon": "-51.2177",
                "display_name": "Praça da Matriz, Porto Alegre, RS, Brasil",
            }
        ]
    )
    mock_cm = mock_urlopen.return_value
    mock_cm.__enter__.return_value = io.BytesIO(body.encode("utf-8"))
    mock_cm.__exit__.return_value = None

    r = client.get(
        "/api/geocoding/search?q=Rua+Mostardeiro+766+Porto+Alegre",
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200
    d = r.get_json()
    assert d["encontrado"] is True
    assert d["latitude"] == -30.0346
    assert d["longitude"] == -51.2177
    assert "Porto Alegre" in d["endereco_exibido"]


@patch("app.routers.geocoding.urllib.request.urlopen")
def test_geocoding_nominatim_vazio(mock_urlopen, client):
    t = register_and_token(client, email="geo3@e.com")
    mock_cm = mock_urlopen.return_value
    mock_cm.__enter__.return_value = io.BytesIO(b"[]")
    mock_cm.__exit__.return_value = None

    r = client.get(
        "/api/geocoding/search?q=xyzzynaoexiste123",
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200
    d = r.get_json()
    assert d["encontrado"] is False
    assert "mensagem" in d
