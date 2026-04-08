include .env_dev


up:
	docker compose up

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up --build

run_migrations:
	docker compose exec app alembic upgrade head

create_migrations:
	docker compose exec app alembic revision --autogenerate -m "$(message)"
	