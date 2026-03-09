<div style="text-align: center;">
    <h1>Pokemon API </h1>
    <img src="./public/pokeball-pokemon-svgrepo-com.svg" width="200" alt="Poetry Logo">
    <p>
        <strong>Powered by</strong>
        <br/>
        <img src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" alt="Poetry Logo" />
        <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastApi Logo" />
        <img src="https://img.shields.io/badge/SQLAlchemy-306998?logo=python&logoColor=white" alt="FastApi Logo" />
    </p>
</div>

## 📚 Visao Geral
API REST para gerenciamento de pokedex, treinadores, batalhas e captura de pokemons.
O projeto foi construido com FastAPI, SQLAlchemy async e estrutura por dominio, mantendo
responsabilidades claras entre rotas, servicos, repositorios e schemas.

## 🧱 Como o projeto foi feito
- **Entrada da aplicacao**: `app/main.py` registra os routers e configura paginacao.
- **Arquitetura por dominio**: cada feature vive em `app/domain/<feature>` com camadas
  de `route`, `service`, `repository` e `schema`.
- **Persistencia async**: SQLAlchemy async com engine configurado em `app/core/database.py`.
- **Configuracoes**: variaveis de ambiente via Pydantic Settings em `app/core/settings.py`.
- **Autenticacao**: JWT com hashing de senha usando `pwdlib[argon2]`.
- **Migracoes**: Alembic para versionamento do banco em `migrations/`.

## 📦 Bibliotecas principais
- **fastapi[standard]**: framework web e servidor de desenvolvimento.
- **sqlalchemy[asyncio]**: ORM async para persistencia.
- **alembic**: migracoes de banco.
- **pydantic-settings**: configuracoes via `.env`.
- **pwdlib[argon2]**: hashing de senha.
- **pyjwt**: tokens JWT.
- **fastapi-pagination**: paginacao nativa.
- **aiosqlite** / **psycopg[binary]**: drivers para SQLite e PostgreSQL.
- **tzdata**: suporte de timezone.

### Ferramentas de desenvolvimento
- **pytest**, **pytest-asyncio**, **pytest-cov**: testes.
- **factory-boy**, **freezegun**: fixtures e datas controladas.
- **testcontainers**: bancos efemeros para testes.
- **ruff**: lint e format.

## 🗂️ Estrutura de pastas
- `app/`: codigo da aplicacao.
- `app/core/`: configuracoes e banco.
- `app/domain/`: features e regras de negocio.
- `app/shared/`: schemas e utilitarios compartilhados.
- `migrations/`: versoes do banco.
- `tests/`: testes automatizados.

## ⚙️ Configuracao
Crie um arquivo `.env` na raiz com as variaveis abaixo:
```env
ALGORITHM=HS256
SECRET_KEY=change-me
DATABASE_URL=sqlite+aiosqlite:///./dev.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Se preferir PostgreSQL, use uma URL semelhante:
```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/pokemon
```

## ▶️ Como usar
### 1) Instalar dependencias
```bash
poetry env use 3.13
poetry install
poetry shell
```

### 2) Rodar migracoes
```bash
alembic upgrade head
```

### 3) Iniciar a API
```bash
fastapi dev app/main.py
```

A API fica disponivel em `http://localhost:8000` e a documentacao em:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## ✅ Testes
```bash
pytest -v
```

## 🧹 Lint e formatacao
```bash
ruff check .
ruff format .
```