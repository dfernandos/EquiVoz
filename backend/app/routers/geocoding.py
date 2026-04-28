"""Geocodificação (endereço → lat/lon) via proxy a Nominatim / OpenStreetMap."""

import json
import logging
import ssl
import urllib.error
import urllib.parse
import urllib.request

import certifi
from flask import Blueprint, jsonify, request

from app.deps import get_current_user

bp = Blueprint("geocoding", __name__)
logger = logging.getLogger(__name__)

# Política de utilização: https://operations.osmfoundation.org/policies/nominatim/
NOMINATIM_SEARCH = "https://nominatim.openstreetmap.org/search"
# Identificar a aplicação (requisito Nominatim)
USER_AGENT = "EquiVoz/1.0 (sistema de registro de ocorrencias; contato no repositorio do projeto)"


@bp.get("/search")
def buscar_por_texto():
    get_current_user()
    q = (request.args.get("q") or "").strip()
    if len(q) < 3:
        return jsonify(detail="Indique um endereço com pelo menos 3 caracteres."), 400
    if len(q) > 400:
        return jsonify(detail="Texto de endereço muito longo."), 400

    params = urllib.parse.urlencode(
        {
            "q": q,
            "format": "json",
            "limit": "1",
            "addressdetails": "0",
            "countrycodes": "br",
        }
    )
    url = f"{NOMINATIM_SEARCH}?{params}"
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    # certifi: evita URLError/SSL "unable to get local issuer certificate" (comum com Python no macOS).
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        logger.warning("Nominatim HTTP %s", e.code)
        return jsonify(
            detail="O serviço de mapas recusou o pedido. Tente novamente em alguns instantes."
        ), 502
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        logger.warning("Nominatim indisponível: %s", e)
        return jsonify(
            detail="Não foi possível acessar o serviço de endereços. Verifique a conexão com a internet e tente novamente."
        ), 502
    except json.JSONDecodeError:
        return jsonify(detail="Resposta inválida do serviço de endereços."), 502

    if not data:
        return (
            jsonify(
                {
                    "encontrado": False,
                    "mensagem": "Não encontramos coordenadas para este texto. Tente: rua, número, bairro e cidade.",
                }
            ),
            200,
        )

    hit = data[0]
    try:
        lat = float(hit["lat"])
        lon = float(hit["lon"])
    except (KeyError, TypeError, ValueError) as e:
        logger.warning("Nominatim resposta inesperada: %s", e)
        return jsonify(detail="Formato de resposta inesperado."), 502

    exib = str(hit.get("display_name", ""))[:500]
    return (
        jsonify(
            {
                "encontrado": True,
                "latitude": lat,
                "longitude": lon,
                "endereco_exibido": exib,
            }
        ),
        200,
    )
