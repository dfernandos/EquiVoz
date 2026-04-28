from datetime import date, datetime, time, timedelta, timezone

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError
from sqlalchemy import String, case, func, literal, or_

from app.database import get_db
from app.deps import get_current_user, get_current_user_optional
from app.email_smtp import send_denuncia_cadastro_confirmacao
from app.models import Denuncia, User
from app.schemas import DenunciaCreate, DenunciaPublic
from app.violation_types import VIOLATION_LABELS, tipos_violacao_payload

bp = Blueprint("denuncias", __name__)


@bp.get("/tipos-violacao")
def tipos_violacao():
    return jsonify(tipos_violacao_payload())


@bp.get("/estatisticas/empresas")
def estatisticas_empresas():
    """Agrupamento por estabelecimento: campo empresa, ou título quando empresa estiver vazio."""
    current_user: User = get_current_user()
    db = get_db()
    try:
        limit = int(request.args.get("limit", 15))
    except ValueError:
        limit = 15
    limit = max(1, min(limit, 50))

    # Denúncias sem "empresa" ainda entram, usando o título como rótulo de agrupamento
    # (ex.: título cita o estabelecimento mas o campo opcional não foi preenchido).
    te = func.trim(Denuncia.empresa)
    tt = func.trim(Denuncia.title)
    nome_agrup = func.coalesce(func.nullif(te, ""), tt)
    rows = (
        db.query(
            nome_agrup.label("empresa"),
            func.count(Denuncia.id).label("total"),
            func.sum(
                case((Denuncia.user_id == current_user.id, 1), else_=0)
            ).label("minhas"),
        )
        .filter(func.length(nome_agrup) > 0)
        .group_by(nome_agrup)
        .order_by(func.count(Denuncia.id).desc())
        .limit(limit)
        .all()
    )
    return jsonify(
        [
            {
                "empresa": r.empresa,
                "total": int(r.total),
                "minhas": int(r.minhas or 0),
            }
            for r in rows
        ]
    )


@bp.get("/estatisticas/dashboard")
def estatisticas_dashboard():
    """KPIs, séries e ranking — dados agregados públicos; campos 'minhas' só com sessão válida."""
    current_user: User | None = get_current_user_optional()
    db = get_db()
    uid = current_user.id if current_user is not None else None

    total = int(db.query(func.count(Denuncia.id)).scalar() or 0)
    com_mapa = int(
        db.query(func.count(Denuncia.id))
        .filter(Denuncia.latitude.isnot(None), Denuncia.longitude.isnot(None))
        .scalar()
        or 0
    )
    minhas_count = (
        int(
            db.query(func.count(Denuncia.id))
            .filter(Denuncia.user_id == current_user.id)
            .scalar()
            or 0
        )
        if current_user is not None
        else 0
    )

    rows_tipo = (
        db.query(Denuncia.violation_type, func.count(Denuncia.id))
        .group_by(Denuncia.violation_type)
        .all()
    )
    por_tipo = [
        {
            "id": v,
            "label": VIOLATION_LABELS.get(v, v),
            "count": int(c),
        }
        for v, c in rows_tipo
    ]
    por_tipo.sort(key=lambda x: -x["count"])

    # Alinha com a lista: mês "efetivo" = data da ocorrência ou, se vazia, do registo (não só created_at).
    data_ref = func.coalesce(Denuncia.occurred_at, Denuncia.created_at)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=400)).replace(tzinfo=None)
    # strftime é SQLite; PostgreSQL usa to_char.
    bind = db.get_bind()
    if bind.dialect.name == "sqlite":
        mes_key = func.strftime("%Y-%m", data_ref)
    else:
        mes_key = func.to_char(data_ref, literal("YYYY-MM", type_=String))
    rows_mes = (
        db.query(mes_key.label("mes"), func.count(Denuncia.id).label("n"))
        .filter(data_ref >= cutoff)
        .group_by(mes_key)
        .order_by(mes_key)
        .all()
    )
    por_mes = [{"mes": r.mes, "registros": int(r.n)} for r in rows_mes]

    te = func.trim(Denuncia.empresa)
    tt = func.trim(Denuncia.title)
    nome_agrup = func.coalesce(func.nullif(te, ""), tt)
    if uid is not None:
        rows_top = (
            db.query(
                nome_agrup.label("empresa"),
                func.count(Denuncia.id).label("total"),
                func.sum(case((Denuncia.user_id == uid, 1), else_=0)).label("minhas"),
            )
            .filter(func.length(nome_agrup) > 0)
            .group_by(nome_agrup)
            .order_by(func.count(Denuncia.id).desc())
            .limit(10)
            .all()
        )
    else:
        rows_top = (
            db.query(nome_agrup.label("empresa"), func.count(Denuncia.id).label("total"))
            .filter(func.length(nome_agrup) > 0)
            .group_by(nome_agrup)
            .order_by(func.count(Denuncia.id).desc())
            .limit(10)
            .all()
        )
    top_empresas = [
        {
            "empresa": r.empresa,
            "total": int(r.total),
            "minhas": int(r.minhas or 0) if uid is not None else 0,
        }
        for r in rows_top
    ]

    return jsonify(
        {
            "total": total,
            "com_localizacao_mapa": com_mapa,
            "minhas": minhas_count,
            "por_tipo": por_tipo,
            "por_mes": por_mes,
            "top_empresas": top_empresas,
        }
    )


def _parse_ymd_arg(name: str) -> date | None:
    raw = (request.args.get(name) or "").strip()
    if not raw:
        return None
    return date.fromisoformat(raw)


@bp.get("")
def list_all_denuncias():
    get_current_user()
    db = get_db()
    q = db.query(Denuncia)

    busca_empresa = (request.args.get("empresa") or "").strip()
    if busca_empresa:
        like = f"%{busca_empresa}%"
        q = q.filter(
            or_(
                Denuncia.empresa.ilike(like),
                Denuncia.title.ilike(like),
                Denuncia.location_text.ilike(like),
            )
        )

    vtype = (request.args.get("violation_type") or "").strip()
    if vtype:
        q = q.filter(Denuncia.violation_type == vtype)

    try:
        data_inicio = _parse_ymd_arg("data_inicio")
        data_fim = _parse_ymd_arg("data_fim")
    except ValueError:
        return jsonify(detail="data_inicio e data_fim devem ser YYYY-MM-DD"), 400

    if data_inicio is not None or data_fim is not None:
        eff = func.coalesce(Denuncia.occurred_at, Denuncia.created_at)
        if data_inicio is not None:
            start_naive = datetime.combine(data_inicio, time.min)
            q = q.filter(eff >= start_naive)
        if data_fim is not None:
            end_naive = datetime.combine(data_fim, time(23, 59, 59, 999999))
            q = q.filter(eff <= end_naive)

    rows = q.order_by(Denuncia.created_at.desc()).all()
    return jsonify([DenunciaPublic.model_validate(r).model_dump(mode="json") for r in rows])


@bp.post("")
def create_denuncia():
    current_user: User = get_current_user()
    try:
        body = DenunciaCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify(detail=e.errors()), 422

    db = get_db()
    denuncia = Denuncia(
        user_id=current_user.id,
        title=body.title.strip(),
        description=body.description.strip(),
        violation_type=body.violation_type.strip(),
        empresa=body.empresa.strip() if body.empresa else None,
        occurred_at=body.occurred_at,
        location_text=body.location_text.strip() if body.location_text else None,
        latitude=body.latitude,
        longitude=body.longitude,
    )
    db.add(denuncia)
    db.commit()
    db.refresh(denuncia)

    send_denuncia_cadastro_confirmacao(
        destinatario_email=current_user.email,
        nome_usuario=current_user.name,
        denuncia_id=denuncia.id,
        titulo=denuncia.title,
        tipo_violacao_exibicao=VIOLATION_LABELS.get(
            denuncia.violation_type, denuncia.violation_type
        ),
        empresa=denuncia.empresa,
        ocorrido_em=denuncia.occurred_at,
        local_texto=denuncia.location_text,
        descricao=denuncia.description,
    )

    return jsonify(DenunciaPublic.model_validate(denuncia).model_dump(mode="json")), 201


@bp.get("/minhas")
def list_my_denuncias():
    current_user: User = get_current_user()
    db = get_db()
    rows = (
        db.query(Denuncia)
        .filter(Denuncia.user_id == current_user.id)
        .order_by(Denuncia.created_at.desc())
        .all()
    )
    return jsonify([DenunciaPublic.model_validate(r).model_dump(mode="json") for r in rows])


@bp.get("/<int:denuncia_id>")
def get_denuncia(denuncia_id: int):
    current_user: User = get_current_user()
    db = get_db()
    row = db.query(Denuncia).filter(Denuncia.id == denuncia_id).first()
    if row is None:
        return jsonify(detail="Denúncia não encontrada"), 404
    if row.user_id != current_user.id:
        return jsonify(detail="Você só pode editar as denúncias que você mesmo registrou."), 403
    return jsonify(DenunciaPublic.model_validate(row).model_dump(mode="json"))


@bp.put("/<int:denuncia_id>")
def update_denuncia(denuncia_id: int):
    current_user: User = get_current_user()
    try:
        body = DenunciaCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify(detail=e.errors()), 422

    db = get_db()
    row = db.query(Denuncia).filter(Denuncia.id == denuncia_id).first()
    if row is None:
        return jsonify(detail="Denúncia não encontrada"), 404
    if row.user_id != current_user.id:
        return jsonify(detail="Você só pode alterar as denúncias que você mesmo registrou."), 403

    row.title = body.title.strip()
    row.description = body.description.strip()
    row.violation_type = body.violation_type.strip()
    row.empresa = body.empresa.strip() if body.empresa else None
    row.occurred_at = body.occurred_at
    row.location_text = body.location_text.strip() if body.location_text else None
    row.latitude = body.latitude
    row.longitude = body.longitude
    db.commit()
    db.refresh(row)
    return jsonify(DenunciaPublic.model_validate(row).model_dump(mode="json"))


@bp.delete("/<int:denuncia_id>")
def delete_denuncia(denuncia_id: int):
    current_user: User = get_current_user()
    db = get_db()
    row = db.query(Denuncia).filter(Denuncia.id == denuncia_id).first()
    if row is None:
        return jsonify(detail="Denúncia não encontrada"), 404
    if row.user_id != current_user.id:
        return jsonify(detail="Você só pode excluir as denúncias que você mesmo registrou."), 403
    db.delete(row)
    db.commit()
    return Response(status=204)
