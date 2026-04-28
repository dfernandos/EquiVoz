"""E2E: criar conta (cadastro + login automático no frontend)."""

import time

from playwright.sync_api import Page, expect


def test_criar_conta_redireciona_autenticado(page: Page, base_url: str, email_unico: str) -> None:
    """Preenche /cadastro, envia e deve ir para a home (/) com sessão (token no localStorage)."""
    page.goto(f"{base_url.rstrip('/')}/cadastro")

    expect(page.get_by_role("heading", name="Criar conta")).to_be_visible()

    page.locator("#name").fill("Usuário novo")
    page.locator("#email").fill(email_unico)
    page.locator("#password").fill("senha-e2e-12")
    page.get_by_role("button", name="Cadastrar e entrar").click()

    expect(page).to_have_url(f"{base_url.rstrip('/')}/", timeout=30_000)
    expect(page.get_by_role("heading", name="EquiVoz", exact=True).first).to_be_visible()
    expect(page.get_by_role("button", name="Sair")).to_be_visible()


def test_criar_conta_email_duplicado_mostra_erro(page: Page, base_url: str) -> None:
    """Segundo cadastro com o mesmo e-mail deve exibir mensagem de erro na página."""
    email = f"dup_{int(time.time() * 1000)}@example.com"

    page.goto(f"{base_url.rstrip('/')}/cadastro")
    page.locator("#name").fill("Primeiro")
    page.locator("#email").fill(email)
    page.locator("#password").fill("senha-e2e-12")
    page.get_by_role("button", name="Cadastrar e entrar").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/", timeout=30_000)

    page.goto(f"{base_url.rstrip('/')}/cadastro")
    page.locator("#name").fill("Segundo")
    page.locator("#email").fill(email)
    page.locator("#password").fill("outra-senha-12")
    page.get_by_role("button", name="Cadastrar e entrar").click()

    expect(page.get_by_role("alert")).to_contain_text("cadastrado", timeout=15_000)
    expect(page).to_have_url(f"{base_url.rstrip('/')}/cadastro")
