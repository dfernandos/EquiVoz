"""E2E: página inicial."""

from playwright.sync_api import Page, expect


def test_home_mostra_titulo_e_links(page: Page, base_url: str) -> None:
    page.goto(base_url)
    expect(page.get_by_role("heading", name="EquiVoz")).to_be_visible()
    # Há dois "Entrar" (topo + área principal); restringimos ao conteúdo principal.
    main = page.locator("main")
    expect(main.get_by_role("link", name="Entrar")).to_be_visible()
    expect(main.get_by_role("link", name="Criar conta")).to_be_visible()


def test_navegacao_para_login(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.locator("main").get_by_role("link", name="Entrar").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/login")
    expect(page.get_by_role("heading", name="Entrar")).to_be_visible()
