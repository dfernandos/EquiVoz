# EquiVoz

Aplicação web para **registo e consulta pública** de ocorrências relacionadas com **discriminação e violação de direitos**, com foco em **minorias sociais**. O sistema oferece autenticação, criação e gestão de denúncias, **estatísticas agregadas** (totais, tendências por mês, tipos de violação, mapa), e apoio à localização (georreferenciação) para análise espacial.

Este repositório contém o **monólito lógico** do produto: API em **Python (Flask)** e interface em **React (Vite)**.

---

## Arquitetura (resumo)

| Camada | Tecnologia | Função |
|--------|------------|--------|
| API REST | Flask 3, SQLAlchemy 2, Pydantic | Autenticação JWT, CRUD de denúncias, estatísticas, integração de geocoding |
| Base de dados | **SQLite** (ficheiro local) ou **PostgreSQL** (variável de ambiente) | Persistência; o esquema é criado ao subir a API |
| Front-end | React 19, React Router, Leaflet, Recharts | Páginas, mapa, gráficos, modos de cor acessíveis |
| Comunicação | `fetch` + proxy do Vite em dev | Chamadas a rotas prefixadas com `/api` |

Em desenvolvimento, o **Vite** reencaminha `/api` para `http://127.0.0.1:8000` (ver `frontend/vite.config.js`).

---

## Estrutura de pastas

```
PythonExampleProject/
├── backend/                 # API Flask
│   ├── app/
│   │   ├── main.py         # fábrica da app, CORS, tabelas na arranque
│   │   ├── config.py       # Settings (pydantic-settings) e .env
│   │   ├── database.py     # engine e sessões
│   │   ├── models.py       # User, Denuncia
│   │   ├── routers/        # auth, denuncias, geocoding
│   │   └── …
│   ├── tests/              # Pytest
│   ├── requirements.txt
│   └── .env.example        # modelo de variáveis (copie para .env)
├── frontend/               # SPA React
│   ├── src/                # componentes, páginas, API client
│   ├── vite.config.js      # proxy /api e Vitest
│   └── package.json
├── .github/workflows/      # CI (GitHub Actions)
└── README.md
```

---

## Requisitos

- **Python** 3.12+ (recomendado; o CI usa 3.12)
- **Node.js** 20+ e npm (para o frontend)
- **PostgreSQL** (opcional): só se quiser deixar de usar SQLite; no macOS com Homebrew, o superutilizador por omissão costuma ser o **teu** utilizador do macOS, não o role `postgres`

---

## Instalação e execução (desenvolvimento)

### 1. Backend (API)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Variáveis de ambiente** — copie o modelo e ajuste:

```bash
cp .env.example .env
```

| Variável | Descrição |
|----------|------------|
| `DATABASE_URL` | **Opcional.** Se estiver vazio ou em falta, o sistema usa SQLite em `./equivoz.db`. Para PostgreSQL, use o formato do exemplo abaixo. Não duplique o nome `DATABASE_URL` na linha. |
| `SECRET_KEY` | Obrigatório em produção: segredo para assinatura de tokens JWT. |
| `ALGORITHM` | Padrão `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token (minutos). |
| `APP_PUBLIC_URL` | URL do site (Netlify, etc.) para o **link de confirmação de e-mail** no registo. Sem isto, o link no e-mail pode apontar para `localhost`. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Envio de e-mail transacional (confirmação de conta). Se `SMTP_HOST` estiver vazio, o registo conclui-se na API mas **nenhum e-mail** é enviado (útil para testes locais; em produção configure um serviço SMTP). |
| `VERIFICACAO_EMAIL_HORAS` | Validade do link de confirmação (padrão 48). |

**Confirmação de e-mail:** após o cadastro, a API envia um link (`/verificar-email?token=…` no front). Só após abrir o link o utilizador pode fazer **login** (`/api/auth/verificar-email`, reenvio em `POST /api/auth/reenviar-verificacao`).

**Exemplos de `DATABASE_URL`:**

- SQLite (implícito se não definir nada, ou explícito): `sqlite:///./equivoz.db`
- PostgreSQL (psycopg3): `postgresql+psycopg://USUÁRIO:SENHA@localhost:5432/equivoz`  
- No **macOS** com Homebrew, provavelmente precisará de algo como `postgresql+psycopg://O_TEU_WHOAMI@localhost:5432/equivoz` (sem a role `postgres` a menos que a crie de propósito).

Crie a base no Postgres se aplicável (ex.: `createdb equivoz`).

**Subir o servidor (porta 8000):**

```bash
python -m app.main
```

Teste: abra `http://127.0.0.1:8000/api/health` e confirme JSON com `"status": "ok"`.

---

### 2. Frontend

Noutro terminal:

```bash
cd frontend
npm install
npm run dev
```

Abra o endereço indicado pelo Vite (normalmente `http://localhost:5173`). As rotas começam por `/api/…` e são servidas em dev via proxy para o backend na **porta 8000**.

**Variáveis no front:**

- `VITE_API_URL` — Em **desenvolvimento** (Vite) pode ficar vazio: o proxy manda `/api` para o backend local. No **build do Netlify** (ou outro *host* só com ficheiros estáticos) é **obrigatório**: URL da API no Heroku, por exemplo `https://o-nome.herokuapp.com`, **sem** barra no fim. Sem isto, o browser chama o próprio site em `/api/...` e obterás **404**.

**Build de produção:**

```bash
npm run build
```

Gera `frontend/dist/`. Nesse cenário, configure o `VITE_API_URL` (ou o servidor a servir a SPA) para o endpoint real da API, e o gateway/CORS de acordo.

---

## Testes

**Backend (na raiz de `backend/`, venv ativo):**

```bash
pytest
```

**Frontend:**

```bash
cd frontend
npm run test
```

**Lint (frontend):**

```bash
npm run lint
```

---

## Integração contínua (GitHub Actions)

O workflow **CI EquiVoz** (`.github/workflows/ci.yml`) corre em *push* e *pull request* às branches `main`, `master` e `develop`, e:

1. **Backend:** instala dependências Python, executa `pytest`.
2. **Frontend:** `npm ci`, `npm run lint`, `npm run test`, `npm run build`.

É necessário que o repositório exista no GitHub com os ficheiros comitados; a aba *Actions* mostra o histórico.

---

## Deploy no Heroku (API / backend)

O repositório tem na **raiz** `requirements.txt`, `.python-version` e `Procfile` para o *buildpack* Python do Heroku detetar a app; o código continua em `backend/`.

1. **Comitar e enviar** estes ficheiros: `requirements.txt`, `.python-version`, `Procfile`, `backend/wsgi.py`.
2. Na app Heroku: adicionar o extra **Heroku Postgres** (ou definir `DATABASE_URL` manualmente). O Heroku injeta `DATABASE_URL` (muitas vezes `postgres://...`); a aplicação já normaliza para o SQLAlchemy.
3. Definir variáveis, por exemplo:
   - `heroku config:set SECRET_KEY="um-segredo-longo-e-aleatório"`
4. **CORS** (obrigatório: o site Netlify e a API Heroku têm domínios diferentes). Na app Heroku:
   ```text
   heroku config:set CORS_ORIGINS="https://equivoz.netlify.app,https://O_HASH--equivoz.netlify.app" -a NOME-DA-APP
   ```
   - Inclui a URL de **produção** do Netlify (`https://equivoz.netlify.app` ou o teu).
   - Inclui também o URL de **Deploy Preview** (o que tem `--` no meio) se usares *branch deploys* / *PR previews* — podes ir acrescentando ou definir a variável com os dois de uma vez (copia o *preview* a partir da barra de endereço quando o build de *preview* abre).
5. Faz *deploy* de novo da API após alterar `CORS_ORIGINS`.

### Netlify (só o front-end)

O repositório inclui `netlify.toml` na **raiz**: o *build* corre em `frontend/`, a pasta publicada no Netlify é `dist` (relativa a `frontend/`, equivalente a `frontend/dist` no repo) e há *redirects* para o React Router (evita 404 em rotas como `/login`).

No painel do Netlify → **Environment variables** → **Add a variable**:

- **Key:** `VITE_API_URL`
- **Value:** a URL pública do Heroku, ex.: `https://equivoz-0d910705aa02.herokuapp.com` (a tua app; **sem** barra no fim)

**Muito importante:** a variável `VITE_API_URL` tem de existir no **âmbito** em que fazes o build. Se abrires o site com um endereço de *Deploy Preview* (`https://xxxxx--equivoz.netlify.app`) mas só definires `VITE_API_URL` em *Production*, o *preview* pode ser construído **sem** a URL do Heroku e o browser continuará a chamar `...netlify.app/api/...` (erro 404 / *Failed to fetch*). **Solução:** no Netlify, em *Environment variables*, seleciona **“Same value for all deploys”** ou adiciona `VITE_API_URL` para **Deploy Previews** e **Branch deploys** com o **mesmo** valor da API no Heroku.

**Site configuration → Build & deploy →** força **Deploys → Clear cache and deploy** após qualquer alteração. O Vite só incorpora `VITE_` no *build*.

Comando local equivalente ao dyno: `gunicorn --chdir backend wsgi:app --bind 0.0.0.0:8000` (o Heroku usa a variável `PORT` automaticamente no `Procfile`).

---

## Segurança e notas

- Nunca comite ficheiro **`.env`** com segredos reais (use `.env.example` só como modelo).
- Em **produção**, use `SECRET_KEY` forte, HTTPS, e PostgreSQL (ou outro SGBD suportado) com cópia de segurança.
- CORS: use a variável `CORS_ORIGINS` no Heroku (ou `.env` local) com a lista de URL do front; o `main.py` junta isso com `localhost` para desenvolvimento.

---

## Licença e apoio

Código do projecto de exemplo; ajuste licença e suporte consoante a vossa equipa. Para problemas técnicos, abra *issues* no repositório ou reúna a equipa interna de desenvolvimento.
