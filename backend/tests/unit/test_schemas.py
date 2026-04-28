"""Testes unitários: validação Pydantic dos DTOs (sem HTTP)."""

import pytest
from pydantic import ValidationError

from app.schemas import DenunciaCreate, LoginRequest, UserCreate


def test_user_create_valid():
    u = UserCreate(email="a@b.com", password="123456", name="Nome")
    assert u.email == "a@b.com"
    assert u.name == "Nome"


def test_user_create_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.com", password="12345", name="X")


def test_login_request_valid():
    LoginRequest(email="x@y.com", password="any")


def test_denuncia_create_valid_minimal():
    d = DenunciaCreate(
        title="Um título ok",
        description="Descrição com pelo menos dez caracteres.",
        violation_type="racismo",
    )
    assert d.latitude is None
    assert d.empresa is None


def test_denuncia_create_com_empresa():
    d = DenunciaCreate(
        title="Um título ok",
        description="Descrição com pelo menos dez caracteres.",
        violation_type="racismo",
        empresa="Habbibs",
    )
    assert d.empresa == "Habbibs"


def test_denuncia_create_title_too_short():
    with pytest.raises(ValidationError):
        DenunciaCreate(
            title="ab",
            description="1234567890ab",
            violation_type="x",
        )
