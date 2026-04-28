# EquiVoz

Aplicação web para **registro e consulta pública** de ocorrências relacionadas a **discriminação e violação de direitos**, com foco em **minorias sociais**. O sistema oferece autenticação, criação e gestão de denúncias, **estatísticas agregadas** (totais, tendências por mês, tipos de violação, mapa) e apoio à localização (georreferenciação) para análise espacial.

**Site publicado (Netlify):** [https://equivoz.netlify.app](https://equivoz.netlify.app)

Este repositório contém o **monólito lógico** do produto: API em **Python (Flask)** e interface em **React (Vite)**.

---

## Arquitetura (resumo)

| Camada | Tecnologia | Função |
|--------|------------|--------|
| API REST | Flask 3, SQLAlchemy 2, Pydantic | Autenticação JWT, CRUD de denúncias, estatísticas, integração de geocoding |
| Banco de dados | **SQLite** (arquivo local) ou **PostgreSQL** (variável de ambiente) | Persistência; o esquema é criado ao subir a API |
| Front-end | React 19, React Router, Leaflet, Recharts | Páginas, mapa, gráficos, modos de cor acessíveis |
| Comunicação | `fetch` + proxy do Vite em dev | Chamadas a rotas prefixadas com `/api` |

Em desenvolvimento, o **Vite** reencaminha `/api` para `http://127.0.0.1:8000` (veja `frontend/vite.config.js`).

---

## Estrutura de pastas

```
PythonExampleProject/
├── backend/                 # API Flask
│   ├── app/
│   │   ├── main.py         # fábrica da app, CORS, tabelas na subida
│   │   ├── config.py       # Settings (pydantic-settings) e .env
│   │   ├── database.py     # engine e sessões
│   │   ├── models.py       # User, Denuncia
│   │   ├── routers/        # auth, denuncias, geocoding
│   │   └── …
│   ├── tests/              # Pytest
│   ├── requirements.txt
│   └── .env.example        # modelo de variáveis (copie para .env)
├── frontend/               # SPA React
│   ├── src/                # componentes, páginas, client da API
│   ├── vite.config.js      # proxy /api e Vitest
│   └── package.json
├── .github/workflows/      # CI (GitHub Actions)
└── README.md
```

---

## Requisitos

- **Python** 3.12+ (recomendado; o CI usa 3.12)
- **Node.js** 20+ e npm (para o front-end)
- **PostgreSQL** (opcional): só se quiser deixar de usar SQLite; no macOS com Homebrew, o superusuário padrão costuma ser o **seu** usuário do macOS, não a role `postgres`

---

## Instalação e execução (desenvolvimento)

### 1. Back-end (API)

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
| `DATABASE_URL` | **Desenvolvimento:** use PostgreSQL (como no `.env.example`) ou, se omitir, SQLite em `./equivoz.db`. **Heroku:** é **obrigatório** PostgreSQL (add-on *Heroku Postgres* define `DATABASE_URL`); a app recusa subir com SQLite no dyno. Não duplique o nome `DATABASE_URL` na linha. |
| `SECRET_KEY` | Obrigatório em produção: segredo para assinatura dos tokens JWT. |
| `ALGORITHM` | Padrão `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token (em minutos). |
| `CORS_ORIGINS` | Origens extras permitidas pelo CORS, separadas por vírgula (veja `.env.example`). |
| `APP_PUBLIC_URL` | URL do site (ex.: `https://equivoz.netlify.app`, sem barra no fim) usada no **link de redefinir senha** enviado por e-mail. |
| `SMTP_*`, `PASSWORD_RESET_TOKEN_HORAS`, `LOG_PASSWORD_RESET_LINK_SEM_SMTP` | Opcionais. **Esqueci a senha:** com SMTP preenchido, a API envia o link; sem SMTP, em produção o usuário precisa de outro meio; em **dev** pode ativar `LOG_PASSWORD_RESET_LINK_SEM_SMTP=true` para ver a URL no log do servidor. |

Após o **cadastro**, a conta fica ativa; o site mostra na página inicial uma **mensagem de confirmação** (sem envio de e-mail pela API; não há SMTP nem verificação por link).

**Esqueci a senha** (`/esqueci-senha` no front; `POST /api/auth/esqueci-senha` e `POST /api/auth/redefinir-senha` na API): a resposta do pedido é **sempre a mesma** (por segurança, não revela se o e-mail existe). O link leva a `/redefinir-senha?token=…`.

**Exemplos de `DATABASE_URL`:**

- SQLite (implícito se não definir nada, ou explícito): `sqlite:///./equivoz.db`
- PostgreSQL (psycopg3): `postgresql+psycopg://USUÁRIO:SENHA@localhost:5432/equivoz`  
- No **macOS** com Homebrew, provavelmente você precisará de algo como `postgresql+psycopg://SEU_USUARIO@localhost:5432/equivoz` (sem a role `postgres`, a menos que a crie de propósito).

Crie o banco no Postgres, se for o caso (ex.: `createdb equivoz`).

**Subir o servidor (porta 8000):**

```bash
python -m app.main
```

Teste: abra `http://127.0.0.1:8000/api/health` e confirme o JSON com `"status": "ok"`.

---

### 2. Front-end

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Abra o endereço indicado pelo Vite (em geral `http://localhost:5173`). As rotas começam com `/api/…` e, em dev, são atendidas via proxy para o back-end na **porta 8000**.

**Variáveis no front:**

- `VITE_API_URL` — Em **desenvolvimento** (Vite) pode ficar vazio: o proxy encaminha `/api` para o back-end local. No **build do Netlify** (ou outro host só com arquivos estáticos) é **obrigatório**: a URL da API no Heroku, por exemplo `https://nome-do-app.herokuapp.com`, **sem** barra no fim. Sem isso, o navegador chama o próprio site em `/api/...` e você recebe **404**.

**Build de produção:**

```bash
npm run build
```

Gera `frontend/dist/`. Nesse cenário, configure o `VITE_API_URL` (ou o servidor que entrega a SPA) para o endpoint real da API e o CORS de acordo.

---

## Testes

**Back-end (na raiz de `backend/`, venv ativo):**

```bash
pytest
```

**Front-end:**

```bash
cd frontend
npm run test
```

**Lint (front-end):**

```bash
npm run lint
```

---

## Integração contínua (GitHub Actions)

O workflow **CI EquiVoz** (`.github/workflows/ci.yml`) roda em *push* e *pull request* nas branches `main`, `master` e `develop`, e:

1. **Back-end:** instala dependências Python, executa `pytest`.
2. **Front-end:** `npm ci`, `npm run lint`, `npm run test`, `npm run build`.

É necessário que o repositório exista no GitHub com os arquivos commitados; a aba *Actions* mostra o histórico.

---

## Deploy no Heroku (API / back-end)

O repositório tem na **raiz** `requirements.txt`, `.python-version` e `Procfile` para o *buildpack* Python do Heroku detectar a app; o código continua em `backend/`.

1. **Commit e push** destes arquivos: `requirements.txt`, `.python-version`, `Procfile`, `backend/wsgi.py`.
2. No app Heroku: adicione o extra **Heroku Postgres** (ou defina `DATABASE_URL` manualmente). O Heroku injeta `DATABASE_URL` (muitas vezes `postgres://...`); a aplicação já normaliza para o SQLAlchemy.
3. Defina variáveis, por exemplo:
   - `heroku config:set SECRET_KEY="um-segredo-longo-e-aleatório"`
4. **CORS** (obrigatório: o site no Netlify e a API no Heroku têm domínios diferentes). No app Heroku:
   ```text
   heroku config:set CORS_ORIGINS="https://equivoz.netlify.app,https://O_HASH--equivoz.netlify.app" -a NOME-DA-APP
   ```
   - Inclua a URL de **produção** do Netlify: [https://equivoz.netlify.app](https://equivoz.netlify.app) (ou a sua, se for outra).
   - Inclua também a URL de **Deploy Preview** (a que tem `--` no meio) se você usar *branch deploys* / *PR previews* — pode adicionar aos poucos ou definir a variável com os dois de uma vez (copie o *preview* da barra de endereço quando o build de *preview* abre).
5. Faça um novo *deploy* da API depois de alterar `CORS_ORIGINS`.

### Netlify (só o front-end)

O repositório inclui `netlify.toml` na **raiz**: o *build* roda em `frontend/`, a pasta publicada no Netlify é `dist` (relativa a `frontend/`, equivalente a `frontend/dist` no repositório) e há *redirects* para o React Router (evita 404 em rotas como `/login`).

Site público: **https://equivoz.netlify.app**

No painel do Netlify → **Environment variables** → **Add a variable**:

- **Key:** `VITE_API_URL`
- **Value:** a URL **da API no Heroku** (termina em **`.herokuapp.com`**). Ex.: `https://equivoz-0d910705aa02.herokuapp.com`. **Não** coloque aqui o endereço do site (`https://…netlify.app`) — isso faz o site chamar a si mesmo e dá 404 / CORS.

**Muito importante:** a variável `VITE_API_URL` precisa existir no **escopo** em que você gera o build. Se abrir o site com um endereço de *Deploy Preview* (`https://xxxxx--equivoz.netlify.app`) mas só definir `VITE_API_URL` em *Production*, o *preview* pode ser construído **sem** a URL do Heroku e o navegador continuará chamando `...netlify.app/api/...` (erro 404 / *Failed to fetch*). **Solução:** no Netlify, em *Environment variables*, selecione **“Same value for all deploys”** ou adicione `VITE_API_URL` para **Deploy Previews** e **Branch deploys** com o **mesmo** valor da API no Heroku.

**Site configuration → Build & deploy →** em *Deploys*, use **Clear cache and deploy** depois de qualquer alteração. O Vite só incorpora `VITE_` no *build*.

Comando local equivalente ao dyno: `gunicorn --chdir backend wsgi:app --bind 0.0.0.0:8000` (o Heroku usa a variável `PORT` automaticamente no `Procfile`).

---

## Segurança e notas

- Nunca commite o arquivo **`.env`** com segredos reais (use `.env.example` só como modelo).
- Em **produção**, use `SECRET_KEY` forte, HTTPS e PostgreSQL (ou outro SGBD suportado) com backup.
- CORS: use a variável `CORS_ORIGINS` no Heroku (ou `.env` local) com a lista de URLs do front; o `main.py` junta isso com `localhost` para desenvolvimento.

---

## Licença e apoio

Código de projeto de exemplo; ajuste licença e suporte conforme a sua equipe. Para problemas técnicos, abra *issues* no repositório ou alinhe com a equipe interna de desenvolvimento.
