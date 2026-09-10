# BHHS VAC — Development Commands
# Run: make <target>

.PHONY: help install dev test check build clean lint format

help:
	@echo "BHHS VAC — Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev           Start dev server (auto-reload)"
	@echo "  make debug         Start dev server with debugger"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run unit tests"
	@echo "  make test-watch    Run tests with watch"
	@echo "  make test-cov      Run tests with coverage"
	@echo "  make e2e           Run end-to-end tests"
	@echo ""
	@echo "Quality:"
	@echo "  make lint          Check code style"
	@echo "  make format        Auto-format code"
	@echo "  make typecheck     Type-check TypeScript"
	@echo "  make check         Run all checks (lint, format, typecheck, test, e2e)"
	@echo ""
	@echo "Build:"
	@echo "  make build         Compile to dist/"
	@echo "  make prod          Build and run production version"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Delete build artifacts, coverage, node_modules"
	@echo "  make setup-hooks   Configure Git hooks"

install:
	npm ci

setup-hooks:
	npx husky install
	npx husky add .husky/pre-commit "npm run precommit"

dev:
	npm run start:dev

debug:
	npm run start:debug

test:
	npm test

test-watch:
	npm run test:watch

test-cov:
	npm run test:cov

e2e:
	npm run test:e2e

lint:
	npm run lint

format:
	npm run format

typecheck:
	npm run typecheck

check:
	npm run check

build:
	npm run build

prod: build
	npm run start:prod

clean:
	npm run clean
