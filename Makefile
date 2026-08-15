COMPOSE := docker compose

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f api

test:
	pytest

lint:
	ruff check app
	mypy app

format:
	ruff format app

migrate:
	alembic upgrade head

seed:
	@echo "Seed data is introduced in the demo-data work unit."

eval:
	@echo "Evaluation workflows are introduced in the quality work unit."
