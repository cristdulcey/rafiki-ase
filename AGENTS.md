# Repository Guidelines

## Project Structure & Module Organization
- Core FastAPI app starts in `src/main.py`; environment defaults live in `src/settings.py`.
- Domain logic split into routers (`src/routers/*`), models and schemas (`src/models`, `src/schemas`), helpers (`src/helpers`), and middlewares (`src/middlewares` for error handling, etc.).
- Persistence and migrations live under `src/alembic` with versions in `src/alembic/versions`; database wiring is in `src/database.py`.
- Static files and templates for any rendered views sit in `src/static` and `src/templates`. GraphQL peer helpers are under `src/rafiki_api`.

## Development Environment, Build & Run
- Prereqs: Docker + Docker Compose, Python 3.11, Poetry.
- Copy or create `.env` (values described in `src/settings.py`; key ones: `SECRET_KEY`, `database_uri`, `SENTRY_DSN`, `add_peer`, `asset_id`).
- Common commands (from repo root):
  - `make up` / `make down` — start/stop the stack via `docker compose`.
  - `make build` — rebuild images; `make push` builds and pushes.
  - `make bash` — shell into the `ase` service container.
  - `make migrate` — create a new Alembic revision; `make apply-migrations` applies to head; `make auth-stamp` stamps a baseline revision.
- Local (without Docker): `cd src && poetry install && uvicorn main:app --reload`.

## Coding Style & Naming Conventions
- Use 4-space indentation, type hints where possible, and prefer descriptive, lower_snake_case module/function names; routers follow feature-based filenames.
- Target Black/PEP 8 formatting; keep imports ordered and minimal.
- API routes should return typed Pydantic schemas; middleware and helpers stay side-effect free where possible.

## Testing Guidelines
- No committed automated suite yet; add pytest tests under `tests/` mirroring router/module names (e.g., `tests/test_accounts.py`).
- Run tests inside the container with `docker compose run --rm ase pytest` or locally via `cd src && pytest`.
- Aim for meaningful coverage on routers, middlewares, and database interactions; include fixtures for external services (TigerBeetle) to keep tests deterministic.

## Commit & Pull Request Guidelines
- Use short, imperative commits similar to existing history (e.g., `add sentry middleware`, `fix path handling`); group related changes per commit.
- PRs should describe scope, risks, and deployment notes; link issues if available and list the commands/tests executed.
- For API changes, include example request/response bodies; for migrations, note expected DB impact and any backfill steps.

## Security & Configuration Tips
- Never commit secrets; rely on `.env`. Rotate keys for `SECRET_KEY`, `idp_secret`, and GraphQL secrets regularly.
- Sentry is optional; if enabled, ensure `SENTRY_DSN` is set before `make up`.
- TigerBeetle client defaults to sync I/O (`TB_CLIENT_IO=sync`) to avoid host restrictions; override only if the target host supports `io_uring`.
