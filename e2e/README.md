# Testes E2E (Playwright + Python + pytest)

Testam o **frontend** React (Vite) no navegador. O Vite encaminha `/api` para o Flask em `http://127.0.0.1:8000`.

## Pré-requisitos

- Python 3.10+ (venv do `e2e/`)
- Node.js + `npm` (para subir o Vite automaticamente)
- Backend com venv em `backend/.venv` (dependências Flask instaladas)
- `playwright install chromium` (uma vez)

## Instalação (uma vez)

```bash
cd e2e
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Como rodar

Com **`pytest` apenas** (recomendado): o `conftest.py` **sobe sozinho** o Flask na **8000** e o Vite na **5173** se essas portas estiverem livres. No fim dos testes, os processos iniciados aqui são encerrados.

```bash
cd e2e
source .venv/bin/activate
pytest
```

Se você **já** tiver Flask e Vite rodando manualmente, o `pytest` **reutiliza** os servidores existentes (não duplica).

### Variáveis de ambiente

| Variável | Efeito |
|----------|--------|
| `E2E_SKIP_SERVERS=1` | Não inicia nada; você precisa ter **8000** e **5173** ativos (comportamento antigo). |

### Opções úteis

- Por padrão o **navegador abre** (`conftest.py` força `headless=False` + `addopts = --headed`). Sem janela (CI): `E2E_HEADLESS=1 pytest` ou `pytest -o addopts=`
- Um arquivo: `pytest tests/test_home.py`
- Outra URL: `pytest --base-url http://127.0.0.1:4173`

## Notas

- Backend **Spring** em outra porta: ajuste o `proxy` em `frontend/vite.config.js` (e suba os serviços manualmente com `E2E_SKIP_SERVERS=1`).
