# Load environment variables
include .env
export

# Colors for terminal messages
YELLOW := \033[1;33m]
GREEN  := \033[1;32m]
RESET  := \033[0m]

.PHONY: help up down reset run_migrations create_migrations install install-dev install-test test test-down test-local clean

# Default target: show help
help:
	@echo "$(YELLOW)Available commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

## ── Docker ──────────────────────────────────────────────────────────────────

up: ## Start development containers
	@echo "$(GREEN)Starting services...$(RESET)"
	docker compose up

down: ## Stop the containers
	@echo "$(YELLOW)Stopping services...$(RESET)"
	docker compose down

reset: ## Remove volumes, rebuild and start
	@echo "$(YELLOW)Resetting Docker environment...$(RESET)"
	docker compose down -v
	docker compose up --build

## ── Database ──────────────────────────────────────────────────────────────

run_migrations: ## Apply Alembic migrations to the latest version
	docker compose exec app alembic upgrade head

create_migrations: ## Generate a new migration. Usage: make create_migrations message="description"
	@if [ -z "$(message)" ]; then \
		echo "$(YELLOW)Error: You must provide a message. Example: make create_migrations message='add_users'$(RESET)"; \
		exit 1; \
	fi
	docker compose exec app alembic revision --autogenerate -m "$(message)"

## ── Installation ────────────────────────────────────────────────────────────

install: ## Install production dependencies
	.venv/bin/pip install -r requirements/base.txt

install-dev: ## Install development dependencies and git hooks
	.venv/bin/pip install -r requirements/dev.txt
	.venv/bin/pre-commit install

install-test: ## Install testing dependencies
	.venv/bin/pip install -r requirements/test.txt

## ── Testing ──────────────────────────────────────────────────────────────────

test: ## Run tests in an isolated Docker environment
	@echo "$(GREEN)Running tests in Docker...$(RESET)"
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@$(MAKE) test-down

test-down: ## Tear down the testing environment
	docker compose -f docker-compose.test.yml down -v

test-local: ## Run tests locally using the venv
	@echo "$(GREEN)Running local tests...$(RESET)"
	.venv/bin/pytest -v --tb=short

## ── Utilities ────────────────────────────────────────────────────────────────

clean: ## Remove Python temporary files and cache
	@echo "$(YELLOW)Cleaning caches...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
