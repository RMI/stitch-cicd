UV ?= uv
DOCKER_COMPOSE := docker compose -f docker-compose.yml
DOCKER_COMPOSE_DEV := $(DOCKER_COMPOSE) -f docker-compose.local.yml
PYTEST := $(UV) run pytest
RUFF := $(UV) run ruff
TEST_PKG := ./scripts/test-package.py

# Aggregate check: can be run in parallel with -j
check: lint test format-check lock-check
	@echo "All checks passed."

lint: py-lint frontend-lint
test: py-test frontend-test
format-check: py-format-check frontend-format-check
lock-check: py-lock-check

format: py-format frontend-format
clean: clean-build py-clean-cache frontend-clean clean-docker

clean-build:
	rm -rf build dist

# ---------------------------------------------------------------------
# Python (UV) infrasturcture
# ---------------------------------------------------------------------

uv-dev: uv-sync-dev
uv-sync-dev:
	$(UV) sync --group dev --all-packages


py-lint: uv-dev
	$(RUFF) check

py-test: api-test pkg-test

py-format-check: uv-dev
	$(RUFF) format --check

py-lock-check:
	$(UV) lock --check

py-format: uv-dev
	$(RUFF) format

py-clean-cache:
	rm -rf .ruff_cache .pytest_cache

uv-sync:
	$(UV) sync

# Generic helpers
uv-test-target:
	$(UV) run --package $(PKG) --active pytest $(PATH) $(ARGS)

uv-test-target-exact:
	$(UV) run --package $(PKG) --active --exact --group dev pytest $(PATH) $(ARGS)

# ---------------------------------------------------------------------
# UV Packages
# ---------------------------------------------------------------------

pkg-test-auth:
	$(UV) run --package stitch-auth pytest packages/stitch-auth
pkg-test-exact-auth:
	$(UV) run --package stitch-auth pytest packages/stitch-auth

pkg-test-models:
	$(UV) run --package stitch-models pytest packages/stitch-models
pkg-test-exact-models:
	$(UV) run --package stitch-models pytest packages/stitch-models

pkg-test-ogsi:
	$(UV) run --package stitch-ogsi pytest packages/stitch-ogsi
pkg-test-exact-ogsi:
	$(UV) run --package stitch-ogsi pytest packages/stitch-ogsi

pkg-test: pkg-test-auth pkg-test-models pkg-test-ogsi
pkg-test-exact: pkg-test-exact-auth pkg-test-exact-models pkg-test-exact-ogsi

# ---------------------------------------------------------------------
# Deployments
# ---------------------------------------------------------------------

api-test:
	$(MAKE) uv-test-target PKG=stitch-api PATH=deployments/api
api-test-exact:
	$(MAKE) uv-test-target-exact PKG=stitch-api PATH=deployments/api

api-dev: stack-api-dev
	POSTGRES_HOST=127.0.0.1 \
	POSTGRES_USER=stitch_app \
	$(UV) run --env-file .env -- \
		uvicorn stitch.api.main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--reload \
		--reload-dir deployments/api/src \
		--reload-dir packages \
		--reload-exclude '*/tests/*'

stack-api-dev:
	SEED_API_BASE_URL=http://host.docker.internal:8000/api/v1 \
	$(DOCKER_COMPOSE_DEV) \
		--profile frontend \
		--profile tools \
		--profile seed \
		up --build \
		-d

# ---------------------------------------------------------------------
# stitch-frontend
# ---------------------------------------------------------------------
FRONTEND_DIR := deployments/stitch-frontend
NPM := npm --prefix $(FRONTEND_DIR)

FRONTEND_PKG  := $(FRONTEND_DIR)/package.json
FRONTEND_LOCK := $(FRONTEND_DIR)/package-lock.json

FRONTEND_INSTALL_STAMP := build/frontend.npm-ci.stamp
FRONTEND_BUILD_STAMP   := build/frontend.build.stamp

# Inputs that should trigger reinstall / rebuild
FRONTEND_INSTALL_INPUTS := $(FRONTEND_PKG) $(FRONTEND_LOCK)

FRONTEND_BUILD_INPUTS := \
	$(FRONTEND_DIR)/index.html \
	$(FRONTEND_DIR)/vite.config.js \
	$(FRONTEND_DIR)/vitest.config.js \
	$(FRONTEND_DIR)/eslint.config.js \
	$(shell find $(FRONTEND_DIR)/src $(FRONTEND_DIR)/public -type f) \
	$(FRONTEND_INSTALL_INPUTS)

frontend: frontend-build

# --- install deps (keyed off lockfile) ---
frontend-install: $(FRONTEND_INSTALL_STAMP)

$(FRONTEND_INSTALL_STAMP): $(FRONTEND_INSTALL_INPUTS)
	mkdir -p $(@D)
	$(NPM) ci
	touch $@

# --- build (incremental) ---
frontend-build: $(FRONTEND_BUILD_STAMP)

$(FRONTEND_BUILD_STAMP): $(FRONTEND_INSTALL_STAMP) $(FRONTEND_BUILD_INPUTS)
	mkdir -p $(@D)
	$(NPM) run build
	touch $@

frontend-test: $(FRONTEND_INSTALL_STAMP)
	$(NPM) run test:run

frontend-lint: $(FRONTEND_INSTALL_STAMP)
	$(NPM) run lint

frontend-format: $(FRONTEND_INSTALL_STAMP)
	$(NPM) run format

frontend-format-check: $(FRONTEND_INSTALL_STAMP)
	$(NPM) run format:check

frontend-dev: $(FRONTEND_INSTALL_STAMP) stack-frontend-dev
	VITE_API_URL=http://localhost:8000/api/v1 \
	$(NPM) run dev

frontend-clean:
	rm -rf $(FRONTEND_DIR)/dist $(FRONTEND_DIR)/node_modules \
	       $(FRONTEND_INSTALL_STAMP) $(FRONTEND_BUILD_STAMP)

# ---------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------
clean-docker:
	$(DOCKER_COMPOSE_DEV) --profile "*" down --volumes --remove-orphans

dev-docker:
	$(DOCKER_COMPOSE_DEV) --profile full up

reboot-docker: clean-docker
	$(DOCKER_COMPOSE_DEV) --profile full up --build

stack-frontend-dev:
	SEED_API_BASE_URL=http://api:8000/api/v1 \
	$(DOCKER_COMPOSE_DEV) \
		--profile api \
		--profile tools \
		--profile seed \
		up --build \
		-d

follow-stack-logs:
	$(DOCKER_COMPOSE_DEV) --profile full logs -f

.PHONY: all build clean \
        build-python \
        check lint test format format-check \
        uv-lint uv-test uv-test-isolated uv-format uv-format-check \
        uv-sync uv-sync-dev uv-sync-all \
        uv-dev \
        clean-build clean-cache \
        lock-check uv-lock-check \
        clean-docker dev-docker \
        frontend frontend-install frontend-build frontend-test frontend-lint frontend-dev frontend-clean frontend-format frontend-format-check
