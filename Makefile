# BEC CRM System Makefile
# Provides common development and deployment commands

.PHONY: help dev prod up down logs migrate seed test clean backup restore

# Default environment
ENV ?= dev

# Help target
help: ## Show this help message
	@echo "BEC CRM System - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment Variables:"
	@echo "  ENV=dev|prod    Set environment (default: dev)"
	@echo ""

# Development Commands
dev: ## Start development environment
	@echo "🚀 Starting BEC CRM in development mode..."
	docker compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d
	@echo "✅ Development environment started!"
	@echo "   📱 Admin UI: http://localhost:5173"
	@echo "   🖥️  Kiosk UI: http://localhost:5173/kiosk"
	@echo "   🔗 API Docs: http://localhost:8000/docs"

prod: ## Start production environment
	@echo "🚀 Starting BEC CRM in production mode..."
	docker compose up -d
	@echo "✅ Production environment started!"
	@echo "   📱 Admin UI: https://krc.bakersfieldesports.com"
	@echo "   🖥️  Kiosk UI: https://kiosk.bakersfieldesports.com"

up: ## Start services (respects ENV variable)
ifeq ($(ENV),prod)
	$(MAKE) prod
else
	$(MAKE) dev
endif

down: ## Stop all services
	@echo "🛑 Stopping BEC CRM services..."
	docker compose -f docker-compose.yml -f docker-compose.override.dev.yml down
	docker compose down
	@echo "✅ Services stopped"

logs: ## View logs from all services
	docker compose logs -f

logs-api: ## View API logs
	docker compose logs -f api

logs-web: ## View web logs
	docker compose logs -f web

logs-worker: ## View worker logs
	docker compose logs -f worker

# Database Commands
migrate: ## Run database migrations
	@echo "📊 Running database migrations..."
	docker compose exec api alembic upgrade head
	@echo "✅ Migrations completed"

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	@if [ -z "$(MSG)" ]; then echo "❌ Please provide a message: make migrate-create MSG='description'"; exit 1; fi
	@echo "📝 Creating new migration: $(MSG)"
	docker compose exec api alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with demo data
	@echo "🌱 Seeding database with demo data..."
	docker compose exec api python /app/scripts/seed_data.py
	@echo "✅ Database seeded successfully"

# Testing Commands
test: ## Run all tests
	@echo "🧪 Running tests..."
	docker compose exec api python -m pytest tests/ -v
	@echo "✅ Tests completed"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	docker compose exec api python -m pytest tests/ -v -m "unit"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	docker compose exec api python -m pytest tests/ -v -m "integration"

test-e2e: ## Run end-to-end tests only
	@echo "🧪 Running E2E tests..."
	docker compose exec api python -m pytest tests/ -v -m "e2e"

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	docker compose exec api python -m pytest tests/ --cov=apps --cov=modules --cov-report=html --cov-report=term

# Backup and Restore Commands
backup: ## Create database backup
	@echo "💾 Creating database backup..."
	docker compose exec api python /app/scripts/backup_restore.py backup
	@echo "✅ Backup created"

backup-name: ## Create named backup (usage: make backup-name NAME="backup_name")
	@if [ -z "$(NAME)" ]; then echo "❌ Please provide a name: make backup-name NAME='backup_name'"; exit 1; fi
	@echo "💾 Creating named backup: $(NAME)"
	docker compose exec api python /app/scripts/backup_restore.py backup --name $(NAME)

restore: ## Restore from backup (usage: make restore BACKUP="backup_file")
	@if [ -z "$(BACKUP)" ]; then echo "❌ Please provide backup file: make restore BACKUP='backup_file'"; exit 1; fi
	@echo "🔄 Restoring from backup: $(BACKUP)"
	docker compose exec api python /app/scripts/backup_restore.py restore $(BACKUP)
	@echo "✅ Restore completed"

list-backups: ## List available backups
	docker compose exec api python /app/scripts/backup_restore.py list

# Maintenance Commands
clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker compose down --volumes --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed"

clean-full: ## Full cleanup including images
	@echo "🧹 Full cleanup of Docker resources..."
	docker compose down --volumes --remove-orphans
	docker system prune -af
	@echo "✅ Full cleanup completed"

# Utility Commands
shell-api: ## Open shell in API container
	docker compose exec api bash

shell-web: ## Open shell in web container
	docker compose exec web sh

shell-worker: ## Open shell in worker container
	docker compose exec worker bash

shell-db: ## Open PostgreSQL shell
	docker compose exec postgres psql -U crm_user -d crm_db

# Build Commands
build: ## Build all Docker images
	@echo "🔨 Building Docker images..."
	docker compose build --no-cache
	@echo "✅ Build completed"

build-api: ## Build API image only
	docker compose build --no-cache api

build-web: ## Build web image only
	docker compose build --no-cache web

build-worker: ## Build worker image only
	docker compose build --no-cache worker

# Health and Status Commands
status: ## Show service status
	docker compose ps

health: ## Check service health
	@echo "🏥 Checking service health..."
	@echo "API Health:"
	@curl -f http://localhost:8000/api/v1/healthz 2>/dev/null || echo "❌ API not responding"
	@echo ""
	@echo "Web Health:"
	@curl -f http://localhost:5173/health 2>/dev/null || echo "❌ Web not responding"
	@echo ""

# Quick start commands
quick-start: ## Quick start for new developers
	@echo "🚀 Quick start for BEC CRM development..."
	@echo "1. 🔨 Building images..."
	$(MAKE) build
	@echo "2. 🚀 Starting development environment..."
	$(MAKE) dev
	@echo "3. ⏳ Waiting for services to be ready..."
	sleep 30
	@echo "4. 📊 Running migrations..."
	$(MAKE) migrate
	@echo "5. 🌱 Seeding demo data..."
	$(MAKE) seed
	@echo ""
	@echo "🎉 Quick start completed!"
	@echo "   📱 Admin UI: http://localhost:5173"
	@echo "   🖥️  Kiosk UI: http://localhost:5173/kiosk"
	@echo "   🔗 API Docs: http://localhost:8000/docs"
	@echo "   👤 Login: admin@bakersfieldesports.com / admin123"

# Production deployment
deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Make sure you have:"
	@echo "   ✅ DNS pointing to this server"
	@echo "   ✅ Ports 80 and 443 open"
	@echo "   ✅ .env file configured"
	@echo ""
	@read -p "Continue with production deployment? [y/N] " confirm && [ "$$confirm" = "y" ]
	$(MAKE) build
	$(MAKE) prod
	sleep 60
	$(MAKE) migrate
	@echo "✅ Production deployment completed!"

# Development workflow
dev-setup: ## Set up development environment
	@echo "🛠️  Setting up development environment..."
	cp .env.example .env.development
	@echo "✅ Created .env.development"
	@echo "📝 Please edit .env.development with your settings"

dev-reset: ## Reset development environment
	@echo "🔄 Resetting development environment..."
	$(MAKE) down
	$(MAKE) clean
	$(MAKE) dev
	sleep 30
	$(MAKE) migrate
	$(MAKE) seed
	@echo "✅ Development environment reset"