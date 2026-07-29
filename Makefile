SHELL := /bin/bash
COMPOSE := docker compose --env-file .env

.PHONY: help init up down restart logs ps test lint migrate shell-web shell-converter build pull deploy clean prod-install prod-deploy prod-status prod-backup

help:
	@printf "Comandos disponíveis:\n"
	@printf "  make init       Cria .env, sobe os serviços, gera APP_KEY e migra\n"
	@printf "  make up         Sobe o ambiente\n"
	@printf "  make down       Para o ambiente\n"
	@printf "  make logs       Acompanha os logs\n"
	@printf "  make test       Executa testes PHP e Python\n"
	@printf "  make deploy     Atualiza o modelo legado na raiz do repositório\n"
	@printf "  make prod-install DOMAIN=https://dominio Instala via deploy/docker\n"
	@printf "  make prod-deploy Executa o deploy Docker/GHCR de produção\n"
	@printf "  make prod-status Exibe o estado da stack de produção\n"
	@printf "  make prod-backup Cria backup PostgreSQL e do .env\n"

init:
	@test -f .env || cp .env.example .env
	$(COMPOSE) up -d --build
	$(COMPOSE) exec -T app php artisan key:generate --force
	$(COMPOSE) exec -T app php artisan migrate --force
	$(COMPOSE) exec -T app php artisan optimize:clear

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build --pull

pull:
	$(COMPOSE) pull

migrate:
	$(COMPOSE) exec -T app php artisan migrate --force

test:
	docker build --target app-test -f apps/web/docker/Dockerfile -t pdf2ofx-app:test .
	docker run --rm pdf2ofx-app:test
	docker build --target test -f services/converter/Dockerfile -t pdf2ofx-converter:test .
	docker run --rm -e PDF2OFX_API_KEY=test-internal-key-123456789 pdf2ofx-converter:test

lint:
	$(COMPOSE) run --rm app sh -lc "find app bootstrap config database routes tests -name '*.php' -print0 | xargs -0 -n1 php -l"
	docker build --target test -f services/converter/Dockerfile -t pdf2ofx-converter:lint .
	docker run --rm --entrypoint ruff pdf2ofx-converter:lint check src tests

shell-web:
	$(COMPOSE) exec app sh

shell-converter:
	$(COMPOSE) exec converter-api sh

deploy:
	bash deploy/scripts/deploy.sh

clean:
	$(COMPOSE) down -v --remove-orphans

prod-install:
	@test -n "$(DOMAIN)" || (echo "Uso: make prod-install DOMAIN=https://dominio [VERSION=1.2.0]" >&2; exit 1)
	bash deploy/docker/install.sh --domain "$(DOMAIN)" --version "$(or $(VERSION),1.2.0)"

prod-deploy:
	bash deploy/docker/deploy.sh

prod-status:
	bash deploy/docker/status.sh

prod-backup:
	bash deploy/docker/backup.sh
