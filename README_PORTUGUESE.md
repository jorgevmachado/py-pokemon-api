[Read in English](./README.md)
<!-- Compatibilidade aprimorada do link de voltar ao topo: Veja: https://github.com/jorgevmachado/py-pokemon-api/pull/73 -->
<a id="readme-top"></a>
<!--
*** Obrigado por conferir o py-pokemon-api. Se você tiver uma sugestão
*** para melhorar este projeto, faça um fork do repositório e crie um pull request
*** ou simplesmente abra uma issue com a tag "enhancement".
*** Não se esqueça de dar uma estrela no projeto!
*** Obrigado novamente! Agora vá criar algo INCRÍVEL! :D
-->

[![GitHub stars](https://img.shields.io/github/stars/jorgevmachado/py-pokemon-api?style=for-the-badge)](https://github.com/jorgevmachado/py-pokemon-api/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/jorgevmachado/py-pokemon-api?style=for-the-badge)](https://github.com/jorgevmachado/py-pokemon-api/network)
[![GitHub issues](https://img.shields.io/github/issues/jorgevmachado/py-pokemon-api?style=for-the-badge)](https://github.com/jorgevmachado/py-pokemon-api/issues)
[![GitHub license](https://img.shields.io/github/license/jorgevmachado/py-pokemon-api?style=for-the-badge)](./LICENSE)
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- LOGO DO PROJETO -->
<br />
<div align="center">
  <a href="https://github.com/jorgevmachado/py-pokemon-api"> 
    <img src="./public/pokeball-pokemon-svgrepo-com.svg" width="200" height="200" alt="Logo">
  </a>

  <h3 align="center">Pokemon API</h3>

  <p align="center">
    <b>Descubra, capture e gerencie Pokémons como nunca antes!</b><br>
    <br>
    <i>py-pokemon-api</i> é uma API RESTful robusta, pronta para produção e pensada para cenários reais. Construída para performance, escalabilidade e segurança, ela permite que desenvolvedores criem, gerenciem e explorem um ecossistema completo de Pokémons com autenticação de usuários, cache avançado e uma arquitetura limpa e sustentável. Seja para jogos, plataformas educacionais ou aplicações orientadas a dados, este projeto oferece uma base sólida e as melhores práticas para desenvolvimento backend moderno.
    <br />
    <a href="https://github.com/jorgevmachado/py-pokemon-api"><strong>Explore a documentação »</strong></a>
    <br />
    <br />
    &middot;
    <a href="https://github.com/jorgevmachado/py-pokemon-api/issues/new?labels=bug&template=bug-report---.md">Reportar Bug</a>
    &middot;
    <a href="https://github.com/jorgevmachado/py-pokemon-api/issues/new?labels=enhancement&template=feature-request---.md">Solicitar Funcionalidade</a>
  </p>
</div>



<!-- SUMÁRIO -->
<details>
  <summary>Sumário</summary>
  <ol>
    <li>
      <a href="#sobre-o-projeto">Sobre o Projeto</a>
      <ul>
        <li><a href="#construido-com">Construído Com</a></li>
        <li><a href="#arquitetura">Arquitetura</a></li>
      </ul>
    </li>
    <li>
      <a href="#primeiros-passos">Primeiros Passos</a>
      <ul>
        <li><a href="#pre-requisitos">Pré-requisitos</a></li>
        <li><a href="#instalacao">Instalação</a></li>
      </ul>
    </li>
    <li><a href="#uso">Uso</a></li>
    <li><a href="#roteiro">Roteiro</a></li>
    <li><a href="#contribuindo">Contribuindo</a></li>
    <li><a href="#decisoes-tecnicas">Decisões Técnicas</a></li>
    <li><a href="#mapa-de-rotas-da-api">Mapa de Rotas da API</a></li>
    <li><a href="#licenca">Licença</a></li>
    <li><a href="#contato">Contato</a></li>
    <li><a href="#agradecimentos">Agradecimentos</a></li>
  </ol>
</details>



<!-- SOBRE O PROJETO -->
<a id="sobre-o-projeto"></a>
## Sobre o Projeto

API REST para gerenciamento de pokedex, treinadores, batalhas e captura de pokémons.
O projeto foi construído com FastAPI, SQLAlchemy async e arquitetura por domínio, mantendo responsabilidades claras entre rotas, serviços, repositórios e schemas.

Principais pontos:
- Estrutura por domínio: cada feature vive em `app/domain/<feature>` com camadas de rota, serviço, repositório e schema.
- Persistência assíncrona: SQLAlchemy async com engine configurado em `app/core/database.py`.
- Configurações: variáveis de ambiente via Pydantic Settings em `app/core/settings.py`.
- Autenticação: JWT com hashing de senha usando `pwdlib[argon2]`.
- Migrações: Alembic para versionamento do banco em `migrations/`.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>


<!-- ARQUITETURA -->
<a id="arquitetura"></a>
## Arquitetura

O projeto segue uma arquitetura limpa e orientada a domínios para garantir manutenibilidade, escalabilidade e separação clara de responsabilidades. Cada funcionalidade é organizada em seu próprio módulo de domínio dentro de `app/domain/<feature>`, contendo:

- **Rotas**: Definem os endpoints da API e tratam as requisições HTTP.
- **Serviços**: Funcionam como orquestradores, coordenando requisições e combinando operações entre as camadas de Business, Repositório e Schema. Os serviços não contêm regras de negócio, mas sim gerenciam o fluxo e integração entre os componentes.
- **Business**: Centralizam as regras de negócio e lógica de domínio. Todas as validações críticas, cálculos e regras específicas do domínio são implementadas aqui, garantindo a integridade e consistência do comportamento da aplicação.
- **Repositórios**: Abstraem o acesso e persistência dos dados, utilizando SQLAlchemy async para operações eficientes de I/O.
- **Schemas**: Definem validação e serialização de dados usando modelos Pydantic.

**Módulos core** (em `app/core/`) fornecem infraestrutura compartilhada, como configuração de banco, autenticação e gerenciamento de settings. O uso de SQLAlchemy async e FastAPI permite alta performance e tratamento não bloqueante das requisições, tornando a API adequada para ambientes de produção com alta concorrência.

**Principais decisões arquiteturais:**
- Isolamento de domínios: cada feature é autocontida, facilitando extensões e refatorações.
- Async-first: todas as operações de banco e I/O são assíncronas para máximo desempenho.
- Configuração via ambiente: todas as settings são gerenciadas por variáveis de ambiente e Pydantic Settings para flexibilidade e segurança.
- Autenticação JWT: autenticação e autorização de usuários de forma segura.
- Migrações Alembic: versionamento confiável do schema do banco de dados.
- Cache (opcional): integração com Redis ou similar para consultas frequentes de baixa latência.

Esta arquitetura é inspirada nas melhores práticas de sistemas backend corporativos, tornando o projeto tanto educativo quanto pronto para uso real.


<!-- MAPA DE ROTAS DA API -->
<a id="mapa-de-rotas-da-api"></a>

## Mapa de Rotas da API

Abaixo está um resumo das principais rotas da API para cada serviço, com uma breve explicação do que cada rota faz:

### Serviço de Autenticação
- `POST /auth/login` — Autentica o usuário e retorna o token JWT
- `POST /auth/register` — Registra um novo usuário

### Serviço de Pokémon (Necessita autenticação)
- `GET /pokemon/` — Lista todos os Pokémons
- `GET /pokemon/{id}` — Detalha um Pokémon específico

### Serviço de Treinador (Necessita autenticação)
- `GET /trainer/` — Lista todos os treinadores
- `GET /trainer/{id}` — Detalha um treinador específico
- `POST /initialize/` — Inicializa um treinador com Pokémon inicial

### Serviço de Pokémons Capturados (Necessita autenticação)
- `GET /captured-pokemons/` — Lista todos os Pokémons do treinador
- `POST /captured-pokemons/capture` — Captura um Pokémon
- `POST /captured-pokemons/heal` — Cura um Pokémon

### Serviço de Pokedex (Necessita autenticação)
- `GET /pokedex/` — Lista todos os Pokémons na Pokédex do treinador
- `POST /pokedex/discover` — Descobre um Pokémon e completa sua Pokédex

### Serviço de Batalha (Necessita autenticação)
- `POST /battle/` — Cria uma nova batalha

> Para a lista completa e detalhes de todos os endpoints, consulte a documentação interativa da API em `/docs` após rodar o projeto.

### 📸 Visualização da API
![Swagger UI](./public/swagger-ui.png)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>


<!-- DECISÕES TÉCNICAS -->
<a id="decisoes-tecnicas"></a>
## ⚙️ Decisões Técnicas

O projeto foi desenvolvido com foco em performance, manutenibilidade e aplicabilidade real. As principais decisões incluem:

- **FastAPI**: escolhida pela alta performance, suporte a async e documentação OpenAPI automática.
- **SQLAlchemy async**: permite controle eficiente de operações I/O-bound e alta concorrência.
- **Alembic**: fornece migrações robustas e versionamento do banco.
- **Pydantic Settings**: simplifica configuração e validação baseada em ambiente.
- **Passlib (argon2)**: hashing seguro de senhas para autenticação de usuários.
- **PyJWT**: gerenciamento de tokens JWT padrão de mercado para autenticação stateless.
- **FastAPI Pagination**: paginação nativa e eficiente para grandes volumes de dados.
- **aiosqlite/psycopg**: drivers assíncronos para SQLite e PostgreSQL, suportando bancos de desenvolvimento e produção.
- **tzdata**: garante tratamento correto de timezone em todos os ambientes.

Essas escolhas equilibram experiência do desenvolvedor, segurança e escalabilidade, tornando o projeto uma base forte para qualquer sistema backend que exija gestão robusta de dados e autenticação de usuários.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>


<a id="construido-com"></a>
### Construído Com

Principais bibliotecas e ferramentas utilizadas:

* [![Poetry][Poetry]][Poetry-url] - Gerenciador de dependências e ambientes Python
* [![FastAPI][FastAPI]][FastAPI-url] - Framework web assíncrono
* [![SQLAlchemy][sqlalchemy]][sqlalchemy-url] - ORM assíncrono para persistência
* [![Alembic][Alembic]][Alembic-url] - Migrações de banco de dados
* [![Pydantic][Pydantic]][Pydantic-url] Settings - Configuração via `.env`
* [![Passlib][Passlib]][Passlib-url] (pwdlib[argon2]) - Hashing de senha
* [![PyJWT][PyJWT]][PyJWT-url] - Tokens JWT
* [![FastAPI Pagination][FastAPIPagination]][FastAPIPagination-url] - Paginação nativa
* [![aiosqlite][aiosqlite]][aiosqlite-url] / [![psycopg][psycopg]][psycopg-url] - Drivers para SQLite e PostgreSQL
* [![tzdata][tzdata]][tzdata-url] - Suporte de timezone

Ferramentas de desenvolvimento:
- pytest, pytest-asyncio, pytest-cov: testes
- factory-boy, freezegun: fixtures e datas controladas
- testcontainers: bancos efêmeros para testes
- ruff: lint e format

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- BADGES & LINKS FOR BUILT WITH -->
[Alembic]: https://img.shields.io/badge/Alembic-23374D?logo=alembic&logoColor=white
[Alembic-url]: https://alembic.sqlalchemy.org/
[Pydantic]: https://img.shields.io/badge/Pydantic-008489?logo=pydantic&logoColor=white
[Pydantic-url]: https://docs.pydantic.dev/latest/
[Passlib]: https://img.shields.io/badge/Passlib-3776AB?logo=python&logoColor=white
[Passlib-url]: https://passlib.readthedocs.io/en/stable/
[PyJWT]: https://img.shields.io/badge/PyJWT-FF9900?logo=python&logoColor=white
[PyJWT-url]: https://pyjwt.readthedocs.io/en/stable/
[FastAPIPagination]: https://img.shields.io/badge/FastAPI--Pagination-005571?logo=fastapi&logoColor=white
[FastAPIPagination-url]: https://github.com/uriyyo/fastapi-pagination
[aiosqlite]: https://img.shields.io/badge/aiosqlite-003B57?logo=sqlite&logoColor=white
[aiosqlite-url]: https://aiosqlite.omnilib.dev/en/latest/
[psycopg]: https://img.shields.io/badge/psycopg-2C5E8A?logo=postgresql&logoColor=white
[psycopg-url]: https://www.psycopg.org/psycopg3/docs/
[tzdata]: https://img.shields.io/badge/tzdata-0A192F?logo=clockify&logoColor=white
[tzdata-url]: https://pypi.org/project/tzdata/


<!-- PRIMEIROS PASSOS -->
<a id="primeiros-passos"></a>
## Primeiros Passos

Para rodar o projeto localmente, siga os passos abaixo para configurar o ambiente, instalar dependências e iniciar a API.

<a id="pre-requisitos"></a>
### Pré-requisitos

1. Python 3.13
2. Poetry instalado ([documentação](https://python-poetry.org/docs/))
3. Banco SQLite (padrão) ou PostgreSQL (opcional)
4. Recomenda-se criar um arquivo `.env` na raiz com as variáveis:
   ```env
   ALGORITHM=HS256
   SECRET_KEY=change-me
   DATABASE_URL=sqlite+aiosqlite:///./dev.db
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
   Para PostgreSQL:
   ```env
   DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/pokemon
   ```
<a id="instalacao"></a>
### Instalação

Você pode usar o Makefile para simplificar a configuração e tarefas comuns:

- Instalar dependências e ativar o ambiente:
  ```bash
  make install
  ```
- Rodar as migrações do banco:
  ```bash
  make migrate
  ```
- Iniciar a API:
  ```bash
  make run
  ```
- Rodar os testes:
  ```bash
  make test
  ```
- Lint e formatação:
  ```bash
  make lint
  make format
  ```

Ou, se preferir, siga os passos manuais abaixo:

1. Clone o repositório:
   ```bash
   git clone https://github.com/jorgevmachado/py-pokemon-api.git
   cd py-pokemon-api
   ```
2. Instale as dependências e ative o ambiente:
   ```bash
   poetry env use 3.13
   poetry install
   poetry shell
   ```
3. Rode as migrações do banco:
   ```bash
   alembic upgrade head
   ```
4. Inicie a API:
   ```bash
   fastapi dev app/main.py
   ```
   A API estará disponível em `http://localhost:8000` e a documentação em:
   - `http://localhost:8000/docs`
   - `http://localhost:8000/redoc`

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- EXEMPLOS DE USO -->
<a id="uso"></a>
## Uso

Exemplo de uso:

Você também pode usar o Makefile para tarefas comuns:

- Rodar a API:
  ```bash
  make run
  ```
- Rodar os testes:
  ```bash
  make test
  ```
- Lint e formatação:
  ```bash
  make lint
  make format
  ```

Ou manualmente:

1. Realize requisições para os endpoints da API para cadastrar, listar, atualizar ou remover pokémons, treinadores e batalhas.
2. Utilize a documentação interativa em `/docs` para explorar e testar os endpoints.

Para rodar os testes:
```bash
pytest -v
```

Para lint e formatação:
```bash
ruff check .
ruff format .
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- ROTEIRO -->
<a id="roteiro"></a>

## Roteiro

- [x] Estrutura por domínio
- [x] Persistência assíncrona
- [x] Autenticação JWT
- [x] Paginação nativa
- [x] Migrações Alembic
- [x] Testes automatizados
- [x] Lint e format

Veja os [open issues](https://github.com/jorgevmachado/py-pokemon-api/issues) para a lista completa de funcionalidades propostas e problemas conhecidos.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- CONTRIBUINDO -->
<a id="contribuindo"></a>
## Contribuindo

Contribuições são bem-vindas! Siga os passos abaixo para colaborar:

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/NomeDaFeature`)
3. Commit suas alterações (`git commit -m 'feat: Descrição da feature'`)
4. Faça push para a branch (`git push origin feature/NomeDaFeature`)
5. Abra um Pull Request

Sugestões de melhorias também podem ser abertas como issues com a tag "enhancement".
Não esqueça de dar uma estrela no projeto!

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- LICENÇA -->
<a id="licenca"></a>
## Licença

Este projeto está licenciado sob a Licença MIT. Você deve dar o devido crédito ao autor (Jorge Machado) em qualquer uso, distribuição ou trabalho derivado.

Veja o arquivo [LICENSE](./LICENSE) para detalhes.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- CONTATO -->
<a id="contato"></a>
## Contato

Jorge Machado - jorge.vmachado@gmail.com

Link do Projeto: [https://github.com/jorgevmachado/py-pokemon-api](https://github.com/jorgevmachado/py-pokemon-api)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- AGRADECIMENTOS -->
<a id="agradecimentos"></a>
## Agradecimentos

Use este espaço para listar recursos que você considera úteis e gostaria de dar crédito. Incluí alguns dos meus favoritos para começar!

* [Escolha uma Licença Open Source](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- LINKS & IMAGENS MARKDOWN -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/jorgevmachado/py-pokemon-api.svg?style=for-the-badge
[contributors-url]: https://github.com/jorgevmachado/py-pokemon-api/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/jorgevmachado/py-pokemon-api.svg?style=for-the-badge
[forks-url]: https://github.com/jorgevmachado/py-pokemon-api/network/members
[stars-shield]: https://img.shields.io/github/stars/jorgevmachado/py-pokemon-api.svg?style=for-the-badge
[stars-url]: https://github.com/jorgevmachado/py-pokemon-api/stargazers
[issues-shield]: https://img.shields.io/github/issues/jorgevmachado/py-pokemon-api.svg?style=for-the-badge
[issues-url]: https://github.com/jorgevmachado/py-pokemon-api/issues
[license-shield]: https://img.shields.io/github/license/jorgevmachado/py-pokemon-api.svg?style=for-the-badge
[license-url]: https://github.com/jorgevmachado/py-pokemon-api/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/jorgevmachado

[Poetry]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json
[Poetry-url]: https://python-poetry.org/
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[sqlalchemy]: https://img.shields.io/badge/SQLAlchemy-306998?logo=python&logoColor=white
[sqlalchemy-url]: https://www.sqlalchemy.org/
[Alembic]: https://img.shields.io/badge/Alembic-23374D?logo=alembic&logoColor=white
[Alembic-url]: https://alembic.sqlalchemy.org/
[Pydantic]: https://img.shields.io/badge/Pydantic-008489?logo=pydantic&logoColor=white
[Pydantic-url]: https://docs.pydantic.dev/latest/
[Passlib]: https://img.shields.io/badge/Passlib-3776AB?logo=python&logoColor=white
[Passlib-url]: https://passlib.readthedocs.io/en/stable/
[PyJWT]: https://img.shields.io/badge/PyJWT-FF9900?logo=python&logoColor=white
[PyJWT-url]: https://pyjwt.readthedocs.io/en/stable/
[FastAPIPagination]: https://img.shields.io/badge/FastAPI--Pagination-005571?logo=fastapi&logoColor=white
[FastAPIPagination-url]: https://github.com/uriyyo/fastapi-pagination
[aiosqlite]: https://img.shields.io/badge/aiosqlite-003B57?logo=sqlite&logoColor=white
[aiosqlite-url]: https://aiosqlite.omnilib.dev/en/latest/
[psycopg]: https://img.shields.io/badge/psycopg-2C5E8A?logo=postgresql&logoColor=white
[psycopg-url]: https://www.psycopg.org/psycopg3/docs/
[tzdata]: https://img.shields.io/badge/tzdata-0A192F?logo=clockify&logoColor=white
[tzdata-url]: https://pypi.org/project/tzdata/




