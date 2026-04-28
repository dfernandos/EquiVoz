"""
Insere 30 denúncias de exemplo (8+8+7+7) para as empresas:
Habbibs, McDonalds, Burguer King, Pizza Hut.

Uso, na pasta backend, com o venv ativo:
    python -m scripts.seed_denuncias

Cria usuários seed1..seed4@equivoz.seed (senha: seedseed12) se ainda não existirem.
Executar de novo adiciona mais 30 linhas; não apaga dados anteriores.
"""
from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta, timezone

from app.auth_utils import hash_password
from app.database import get_session_factory
from app.main import create_app
from app.models import Denuncia, User
from app.violation_types import VIOLATION_LABELS

# Pedido: “Burguer” no nome do BK
EMPRESAS_E_QUANTIDADE: list[tuple[str, int]] = [
    ("Habbibs", 8),
    ("McDonalds", 8),
    ("Burguer King", 7),
    ("Pizza Hut", 7),
]

TIPOS = list(VIOLATION_LABELS.keys())

TITULOS = [
    "Problema no atendimento — {empresa}",
    "Experiência negativa na {empresa}",
    "Relato de discriminação — unidade {empresa}",
    "Falta de acessibilidade no {empresa}",
    "Situação desconfortável no balcão da {empresa}",
    "Não fui respeitado no {empresa}",
    "Demora excessiva no {empresa}",
    "Funcionamento irregular — {empresa}",
]

FRASES_DESC = [
    "Relato para popular a base de testes do EquiVoz, com dados plausíveis e anônimos.",
    "Descrevo a situação com o detalhe que o contexto permitir neste registro.",
    "Outras pessoas estavam presentes e podem corroborar partes do ocorrido.",
    "O atendimento ocorreu em horário de movimento intenso no estabelecimento.",
    "Gostaria de medidas para evitar repetição deste tipo de ocorrência.",
    "O encarregado da loja foi informado verbalmente no mesmo dia.",
    "Evidências adicionais podem ser requisitadas se as autoridades assim o entenderem.",
    "Peço o devido arquivamento desta denúncia e eventual seguimento.",
]

BAIRROS = [
    "Centro, POA/RS",
    "Cristal, Porto Alegre",
    "Bela Vista, São Paulo/SP",
    "Copacabana, Rio de Janeiro/RJ",
    "Asa Sul, Brasília/DF",
]


def _random_titulo(empresa: str) -> str:
    return random.choice(TITULOS).format(empresa=empresa)[:500]


def _random_desc() -> str:
    t = " ".join(random.choices(FRASES_DESC, k=random.randint(2, 3)))
    if len(t) < 50:
        t += " Relato concluído."
    return t


def _random_occurred() -> datetime:
    return (datetime.now(timezone.utc) - timedelta(
        days=random.randint(10, 600),
        hours=random.randint(0, 20),
    )).replace(tzinfo=None)


def _random_lat_lng() -> tuple[float, float]:
    # Aprox. região sul/sudeste BR
    lat = random.uniform(-30.2, -22.8)
    lng = random.uniform(-51.4, -43.1)
    return round(lat, 6), round(lng, 6)


def _get_or_create_seed_users(db) -> list[User]:
    emails = [f"seed{i}@equivoz.seed" for i in range(1, 5)]
    out: list[User] = []
    for email in emails:
        u = db.query(User).filter(User.email == email).first()
        if u is None:
            u = User(
                email=email,
                name=f"Conta {email.split('@')[0]}",
                hashed_password=hash_password("seedseed12"),
            )
            db.add(u)
    db.commit()
    for email in emails:
        out.append(db.query(User).filter(User.email == email).one())
    return out


def run() -> int:
    create_app()
    Session = get_session_factory()
    db = Session()
    try:
        users = _get_or_create_seed_users(db)
        if not users:
            print("Erro: nenhum usuário seed.", file=sys.stderr)
            return 1
        n = 0
        for empresa, q in EMPRESAS_E_QUANTIDADE:
            for _ in range(q):
                u = random.choice(users)
                lat, lng = _random_lat_lng() if random.random() > 0.1 else (None, None)
                d = Denuncia(
                    user_id=u.id,
                    title=_random_titulo(empresa),
                    description=_random_desc(),
                    violation_type=random.choice(TIPOS),
                    empresa=empresa,
                    occurred_at=_random_occurred() if random.random() > 0.15 else None,
                    location_text=random.choice(BAIRROS) if random.random() > 0.2 else None,
                    latitude=lat,
                    longitude=lng,
                )
                db.add(d)
                n += 1
        db.commit()
        print(f"Inseridas {n} denúncias (empresas: {', '.join(e for e, _ in EMPRESAS_E_QUANTIDADE)}).")
        print("Usuários de teste: seed1..seed4@equivoz.seed | senha: seedseed12")
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
