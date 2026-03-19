lint:
	poetry run ruff check
lint-fix:
	poetry run ruff check --fix
lint-format:
	poetry run ruff format
format:
	poetry run make lint-fix
	poetry run make lint-format

test-app:
	poetry run pytest -x --cov=app -vv
test-coverage:
	poetry run coverage html
test:
	make lint
	make test-app
	make test-coverage

dev:
	poetry run fastapi dev app/main.py

run:
	make dev

create-migration:
	@if [ -z "$(message)"]; then \
  		echo "Error: message variable is required. Usage: make create-migration message='Your migration message'"; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(message)"

rollback-migration:
	poetry run alembic downgrade -1

migrate:
	poetry run alembic upgrade head



