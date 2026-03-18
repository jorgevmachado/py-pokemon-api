[Leia em Português](./README_PORTUGUESE.md)

<!-- Improved compatibility of back to top link: See: https://github.com/jorgevmachado/py-pokemon-api/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the py-pokemon-api. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

[![GitHub stars](https://img.shields.io/github/stars/jorgevmachado/py-pokemon-api?style=for-the-badge)](https://github.com/jorgevmachado/py-pokemon-api/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/jorgevmachado/py-pokemon-api?style=for-the-badge)](https://github.com/jorgevmachado/py-pokemon-api/network)
[![GitHub issues](https://img.shields.io/github/issues/jorgevmachado/py-pokemon-api?style=for-the-badge)](https://github.com/jorgevmachado/py-pokemon-api/issues)
[![GitHub license](https://img.shields.io/github/license/jorgevmachado/py-pokemon-api?style=for-the-badge)](./LICENSE)
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/jorgevmachado/py-pokemon-api"> 
    <img src="./public/pokeball-pokemon-svgrepo-com.svg" width="200" height="200" alt="Logo">
  </a>

  <h3 align="center">Pokemon API</h3>

  <p align="center">
    A simple API to get information about Pokemon.
    <br />
    <a href="https://github.com/jorgevmachado/py-pokemon-api"><strong>Explore the docs »</strong></a>
    <br />
    <br /> 
    &middot;
    <a href="https://github.com/jorgevmachado/py-pokemon-api/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/jorgevmachado/py-pokemon-api/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

REST API for managing pokedex, trainers, battles, and pokemon capture.
The project was built with FastAPI, async SQLAlchemy, and domain-driven architecture, keeping clear responsibilities between routes, services, repositories, and schemas.

Main points:
- Domain structure: each feature lives in `app/domain/<feature>` with route, service, repository, and schema layers.
- Async persistence: async SQLAlchemy with engine configured in `app/core/database.py`.
- Settings: environment variables via Pydantic Settings in `app/core/settings.py`.
- Authentication: JWT with password hashing using `pwdlib[argon2]`.
- Migrations: Alembic for database versioning in `migrations/`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

Main libraries and tools used:

* [![Poetry][Poetry]][Poetry-url] - Python dependency and environment manager
* [![FastAPI][FastAPI]][FastAPI-url] - Asynchronous web framework
* [![SQLAlchemy][sqlalchemy]][sqlalchemy-url] - Async ORM for persistence
* [![Alembic][Alembic]][Alembic-url] - Database migrations
* [![Pydantic][Pydantic]][Pydantic-url] Settings - Configuration via `.env`
* [![Passlib][Passlib]][Passlib-url] (pwdlib[argon2]) - Password hashing
* [![PyJWT][PyJWT]][PyJWT-url] - JWT tokens
* [![FastAPI Pagination][FastAPIPagination]][FastAPIPagination-url] - Native pagination
* [![aiosqlite][aiosqlite]][aiosqlite-url] / [![psycopg][psycopg]][psycopg-url] - Drivers for SQLite and PostgreSQL
* [![tzdata][tzdata]][tzdata-url] - Timezone support

Development tools:
- pytest, pytest-asyncio, pytest-cov: tests
- factory-boy, freezegun: fixtures and controlled dates
- testcontainers: ephemeral databases for tests
- ruff: lint and format

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To run the project locally, follow the steps below to set up the environment, install dependencies, and start the API.

### Prerequisites

1. Python 3.13
2. Poetry installed ([documentation](https://python-poetry.org/docs/))
3. SQLite database (default) or PostgreSQL (optional)
4. It is recommended to create a `.env` file at the root with the variables:
   ```env
   ALGORITHM=HS256
   SECRET_KEY=change-me
   DATABASE_URL=sqlite+aiosqlite:///./dev.db
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
   For PostgreSQL:
   ```env
   DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/pokemon
   ```
### Installation

You can use the Makefile to simplify setup and common tasks:

- Install dependencies and activate environment:
  ```bash
  make install
  ```
- Run database migrations:
  ```bash
  make migrate
  ```
- Start the API:
  ```bash
  make run
  ```
- Run tests:
  ```bash
  make test
  ```
- Lint and format:
  ```bash
  make lint
  make format
  ```

Or, if you prefer, follow the manual steps below:

1. Clone the repository:
   ```bash
   git clone https://github.com/jorgevmachado/py-pokemon-api.git
   cd py-pokemon-api
   ```
2. Install dependencies and activate the environment:
   ```bash
   poetry env use 3.13
   poetry install
   poetry shell
   ```
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the API:
   ```bash
   fastapi dev app/main.py
   ```
   The API will be available at `http://localhost:8000` and the documentation at:
   - `http://localhost:8000/docs`
   - `http://localhost:8000/redoc`

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Usage example:

You can also use the Makefile for common tasks:

- Run the API:
  ```bash
  make run
  ```
- Run tests:
  ```bash
  make test
  ```
- Lint and format:
  ```bash
  make lint
  make format
  ```

Or manually:

1. Make requests to the API endpoints to create, list, update, or delete pokémons, trainers, and battles.
2. Use the interactive documentation at `/docs` to explore and test the endpoints.

To run the tests:
```bash
pytest -v
```

For lint and formatting:
```bash
ruff check .
ruff format .
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Domain structure
- [x] Async persistence
- [x] JWT authentication
- [x] Native pagination
- [x] Alembic migrations
- [x] Automated tests
- [x] Lint and format

See the [open issues](https://github.com/jorgevmachado/py-pokemon-api/issues) for the full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome! Follow the steps below to collaborate:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/FeatureName`)
3. Commit your changes (`git commit -m 'feat: Feature description'`)
4. Push to the branch (`git push origin feature/FeatureName`)
5. Open a Pull Request

Suggestions for improvements can also be opened as issues with the tag "enhancement".
Don't forget to star the project!

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

This project is licensed under the MIT License. You must give appropriate credit to the author (Jorge Machado) in any use, distribution, or derivative work.

See the [LICENSE](./LICENSE) file for details.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Jorge Machado - jorge.vmachado@gmail.com

Project Link: [https://github.com/jorgevmachado/py-pokemon-api](https://github.com/jorgevmachado/py-pokemon-api)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
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

