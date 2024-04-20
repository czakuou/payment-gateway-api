.PHONY: tests

format:
	ruff check --fix --exit-non-zero-on-fix --show-fixes --preview
	black src $(ARGS)

lint:
	ruff check
	black --check .
	mypy .

up:
	@docker compose up app

down:
	@docker-compose down $(ARGS)

bash:
	@docker compose -f docker-compose.yml run --rm app bash

migrate:
	@docker compose run --rm alembic revision --autogenerate -m "$(message)"

upgrade:
	@docker compose run --rm alembic upgrade head

downgrade:
	@docker compose run --rm alembic downgrade -1

tests:
	@docker compose run tests

test:
	@docker compose run tests -o log_cli=true $(flags) -k $(t)

logs:
	@docker compose logs -f

start:
	@docker compose down
	@docker system prune -a
	@docker compose build
	@docker compose up app -d

build:
	@docker compose build
