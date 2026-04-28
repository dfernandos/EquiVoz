"""Testes unitários: regras de tipos de violação (sem Flask/HTTP)."""

from app.violation_types import VIOLATION_LABELS, tipos_violacao_payload


def test_violation_labels_contains_racismo_and_outro():
    assert "racismo" in VIOLATION_LABELS
    assert "outro" in VIOLATION_LABELS
    assert len(VIOLATION_LABELS) == 8


def test_tipos_violacao_payload_shape_and_order():
    payload = tipos_violacao_payload()
    assert len(payload) == 8
    assert all("id" in item and "label" in item for item in payload)
    assert payload[0]["id"] == "racismo"
    assert {item["id"] for item in payload} == set(VIOLATION_LABELS.keys())
