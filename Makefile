up:
	docker compose up --remove-orphans

down:
	docker compose down

build:
	docker compose build

push:
	docker compose build --push

auth-stamp:
	docker compose run --rm ase alembic stamp c8b2e4f3bd86

apply-migrations:
	docker compose run --rm ase alembic upgrade head

migrate:
	docker compose run --rm ase alembic revision --autogenerate -m "migration"

bash:
	docker compose run --rm ase bash

poetry:
	cd src && poetry update && rm -rf .venv && cd ..
# 	docker compose build
