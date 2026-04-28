"""E2E: cadastro e denúncia (requer API Flask em :8000 atrás do proxy do Vite)."""

from playwright.sync_api import Page, expect


def test_cadastro_e_denuncia_happy_path(page: Page, base_url: str, email_unico: str) -> None:
    page.goto(f"{base_url.rstrip('/')}/cadastro")
    page.locator("#name").fill("Usuário E2E")
    page.locator("#email").fill(email_unico)
    page.locator("#password").fill("e2e-secret-12")
    page.get_by_role("button", name="Cadastrar e entrar").click()

    expect(page).to_have_url(f"{base_url.rstrip('/')}/", timeout=30_000)
    page.get_by_role("link", name="Nova denúncia").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/denuncia", timeout=30_000)
    expect(page.get_by_role("heading", name="Registrar ocorrência")).to_be_visible()

    page.wait_for_selector("#violation_type option", state="attached", timeout=30_000)

    page.locator("#title").fill("Ocorrência registrada via Playwright")
    page.locator("#description").fill(
        "Descrição automática com mais de dez caracteres para validar o fluxo E2E."
    )
    page.get_by_role("button", name="Registrar denúncia").click()

    expect(page.get_by_role("status")).to_contain_text("Denúncia registrada com sucesso", timeout=30_000)


def test_login_apos_logout(page: Page, base_url: str, email_unico: str) -> None:
    email = f"logout_{email_unico}"
    page.goto(f"{base_url.rstrip('/')}/cadastro")
    page.locator("#name").fill("E2E Logout")
    page.locator("#email").fill(email)
    page.locator("#password").fill("e2e-secret-12")
    page.get_by_role("button", name="Cadastrar e entrar").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/", timeout=30_000)

    page.goto(f"{base_url.rstrip('/')}/")
    page.get_by_role("button", name="Sair").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/")

    page.goto(f"{base_url.rstrip('/')}/login")
    page.locator("#email").fill(email)
    page.locator("#password").fill("e2e-secret-12")
    page.get_by_role("button", name="Entrar").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/", timeout=30_000)
