# AVA Microservices Makefile
# Comandos para gerenciar o ecossistema de microserviços

.PHONY: help up down logs ps seed clean build dev prod

help: ## Mostra esta ajuda
	@echo "AVA Microservices - Comandos Disponíveis"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "Exemplos:"
	@echo "  make up          # Inicia todos os serviços"
	@echo "  make down        # Para todos os serviços"
	@echo "  make logs        # Mostra logs de todos os serviços"
	@echo "  make seed        # Executa seed data nos serviços"

# Sobe toda a stack
up: ## Inicia todos os serviços
	docker compose up -d

down: ## Para todos os serviços
	docker compose down

logs: ## Mostra logs de todos os serviços
	docker compose logs -f

# Dev por serviço (isolado)
up-gateway: ## Inicia apenas o API Gateway
	docker compose -f api-gateway/docker-compose.dev.yml up -d

up-auth: ## Inicia apenas o Auth Service
	docker compose -f auth_service/docker-compose.dev.yml up -d

up-learning: ## Inicia apenas o Learning Service
	docker compose -f learning_service/docker-compose.dev.yml up -d

up-rec: ## Inicia apenas o Recommendation Service
	docker compose -f recommendation_service/docker-compose.dev.yml up -d

logs-auth: ## Mostra logs do auth_service
	docker compose logs -f auth_service

logs-learning: ## Mostra logs do learning_service
	docker compose logs -f learning_service

logs-recommendation: ## Mostra logs do recommendation_service
	docker compose logs -f recommendation_service

logs-gateway: ## Mostra logs do api-gateway
	docker compose logs -f api-gateway

ps: ## Mostra status dos containers
	docker compose ps

build: ## Constrói todas as imagens
	docker compose build

build-no-cache: ## Constrói todas as imagens sem cache
	docker compose build --no-cache

dev: ## Inicia em modo desenvolvimento
	docker compose up -d --build

prod: ## Inicia em modo produção
	docker compose up -d --build

seed: ## Executa seed data nos serviços
	docker compose exec auth_service python manage.py seed_data || echo "Erro no seed do auth_service"
	docker compose exec learning_service python manage.py seed_data || echo "Erro no seed do learning_service"

migrate: ## Executa migrações nos serviços
	docker compose exec auth_service python manage.py migrate
	docker compose exec learning_service python manage.py migrate

createsuperuser: ## Cria superusuário nos serviços Django
	docker compose exec auth_service python manage.py createsuperuser --noinput --username admin --email admin@example.com || echo "Superusuário já existe no auth_service"
	docker compose exec learning_service python manage.py createsuperuser --noinput --username admin --email admin@example.com || echo "Superusuário já existe no learning_service"

restart: ## Reinicia todos os serviços
	docker compose restart

restart-auth: ## Reinicia auth_service
	docker compose restart auth_service

restart-learning: ## Reinicia learning_service
	docker compose restart learning_service

restart-recommendation: ## Reinicia recommendation_service
	docker compose restart recommendation_service

restart-gateway: ## Reinicia api-gateway
	docker compose restart api-gateway

clean: ## Remove containers, volumes e imagens
	docker compose down -v --rmi all

clean-volumes: ## Remove apenas os volumes
	docker compose down -v

shell-auth: ## Acessa shell do auth_service
	docker compose exec auth_service bash

shell-learning: ## Acessa shell do learning_service
	docker compose exec learning_service bash

shell-recommendation: ## Acessa shell do recommendation_service
	docker compose exec recommendation_service bash

test: ## Executa testes nos serviços
	docker compose exec auth_service python manage.py test
	docker compose exec learning_service python manage.py test

status: ## Mostra status detalhado dos serviços
	docker compose ps

health: ## Verifica health dos serviços
	curl -s http://localhost:4200/healthz || echo "Frontend não está respondendo"
	curl -s http://localhost:8080/healthz || echo "API Gateway não está respondendo"
	curl -s http://localhost:8001/healthz/ || echo "Auth Service não está respondendo"
	curl -s http://localhost:8002/healthz/ || echo "Learning Service não está respondendo"
	curl -s http://localhost:8003/healthz || echo "Recommendation Service não está respondendo"

# --- Frontend Commands ---
.PHONY: frontend-install frontend-dev frontend-build frontend-test frontend-lint frontend-clean
frontend-install: ## Instala dependências do frontend
	@echo "$(GREEN)Instalando dependências do frontend...$(NC)"
	cd ava-frontend && npm install

frontend-dev: ## Inicia servidor de desenvolvimento do frontend
	@echo "$(GREEN)Iniciando servidor de desenvolvimento do frontend...$(NC)"
	cd ava-frontend && npm run dev

frontend-build: ## Build do frontend para produção
	@echo "$(GREEN)Build do frontend para produção...$(NC)"
	cd ava-frontend && npm run build:prod

frontend-test: ## Executa testes do frontend
	@echo "$(GREEN)Executando testes do frontend...$(NC)"
	cd ava-frontend && npm test

frontend-lint: ## Executa linter do frontend
	@echo "$(GREEN)Executando linter do frontend...$(NC)"
	cd ava-frontend && npm run lint

frontend-clean: ## Limpa artefatos de build do frontend
	@echo "$(GREEN)Limpando artefatos de build do frontend...$(NC)"
	cd ava-frontend && rm -rf dist node_modules/.cache

# Comando padrão
.DEFAULT_GOAL := help
