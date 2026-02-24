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

## 📚 Visão Geral

## Projeto
```bash
   poetry env use 3.13
   poetry env activate
   source /home/jorge.machado/.cache/pypoetry/virtualenvs/fast-zero-dVL4rHQI-py3.13/bin/activate
```

## 🚀 Tecnologias Utilizadas
### FastAPI
#### Ferramenta para criar APIs
```bash
   poetry add fastapi[standard]
   fastapi dev app/main.py
   pytest tests/app/domain/pokemon/external/test_external_service.py -v
   pytest tests/app/domain/pokemon/external/test_external_business.py -v
   pytest tests/app/domain/pokemon/external/test_external_service.py::TestPokemonExternalServiceFetchByName::test_pokemon_external_fetch_by_name_not_pokemon_specie -v
   pytest tests/app/domain/pokemon/external/test_external_service.py::TestPokemonExternalServiceByName::test_pokemon_external_by_name_success -v
```
### sqlalchemy
#### Ferramenta para gerenciamento de banco de dados
```bash
   poetry add sqlalchemy
```
### sqlalchemy[asyncio]
#### Ferramenta para gerenciamento de banco de dados com async
```bash
   poetry add "sqlalchemy[asyncio]"
```
### aiosqlite
#### Ferramenta para gerenciamento de banco de dados sqlite com async
```bash
   poetry add aiosqlite
```
### pydantic-settings
#### Ferramenta para gerenciamento de configurações usando Pydantic
```bash
   poetry add pydantic-settings
```
### Pytest
#### Ferramenta para testes automatizados
```bash
   poetry add --group dev pytest pytest-cov
```
### pwdlib
#### Ferramenta para gerenciamento de senhas
```bash
   poetry add "pwdlib[argon2]"
```
### JWT
#### Ferramenta para gerar tokens JWT
```bash
   poetry add pyjwt
```
### tzdata
#### Ferramenta para gerenciamento de fuso horário
```bash
   poetry add tzdata
```
### pytest-asyncio
#### Ferramenta para testes assíncronos
```bash
   poetry add --group dev pytest-asyncio
```
### factory-boy
#### Ferramenta para gerar dados falsos
```bash
   poetry add --group dev factory-boy
```
### freezegun
#### Ferramenta para gerar datas falsas
```bash
   poetry add --group dev freezegun
```
### psycopg[binary]
#### Ferramenta para gerenciamento de banco de dados postgresql
```bash
   poetry add "psycopg[binary]"
```
### testcontainers
#### Ferramenta para gerenciamento de banco de dados docker
```bash
   poetry add --group dev testcontainers
```
### alembic
#### Ferramenta para gerenciamento de migrações de dados de banco de dados
```bash
   poetry add alembic
   // Cria a estrutura de pastas de migração.
   alembic init migrations
   // cria uma versão de dados.
   alembic revision --autogenerate -m "create users table"
   // Atualiza para a ultima versão.
   alembic upgrade head
   // Volta uma versão.
   alembic downgrade -1
   // Cria uma migração versão vazia, sem autogenerate
   alembic revision -m "create seeds"
   
```