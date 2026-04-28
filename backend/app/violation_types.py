"""Tipos de violação — lógica pura, reutilizável em rotas e testes unitários."""

VIOLATION_LABELS: dict[str, str] = {
    "racismo": "Racismo",
    "discriminacao_genero": "Discriminação de gênero",
    "discriminacao_orientacao": "Discriminação por orientação sexual",
    "discriminacao_religiosa": "Discriminação religiosa",
    "discriminacao_deficiencia": "Discriminação por deficiência",
    "violencia": "Violência",
    "servico_publico": "Serviço público (educação, saúde, segurança)",
    "outro": "Outro",
}


def tipos_violacao_payload() -> list[dict[str, str]]:
    """Lista no formato da API GET /api/denuncias/tipos-violacao."""
    return [{"id": k, "label": v} for k, v in VIOLATION_LABELS.items()]
