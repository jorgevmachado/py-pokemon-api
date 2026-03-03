lint:
	ruff check
lint-fix:
	ruff check --fix
lint-format:
	ruff format
format:
	make lint-fix
	make lint-format

test-app:
	pytest -x --cov=app -vv
test-coverage:
	coverage html
test:
	make lint
	make test-app
	make test-coverage

dev:
	fastapi dev app/main.py