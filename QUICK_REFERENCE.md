# Quick Reference - Environment Commands

## Development Environment

```bash
# Start development
docker-compose -f docker-compose.dev.yml up -d

# Stop development
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Rebuild and restart
docker-compose -f docker-compose.dev.yml up -d --build

# Check status
docker-compose -f docker-compose.dev.yml ps

# Reset development database (DELETES ALL DEV DATA!)
docker-compose -f docker-compose.dev.yml down
docker volume rm crm_postgres_data_dev crm_redis_data_dev
docker-compose -f docker-compose.dev.yml up -d
```

## Production Environment

```bash
# Start production
docker-compose -f docker-compose.prod.yml up -d

# Stop production (CAREFUL!)
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# Backup production database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U crm_prod_user crm_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Current Environment (Legacy)

```bash
# This uses docker-compose.yml (currently your active dev setup)
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose ps
```

## Switching Environments

```bash
# From dev to prod
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.prod.yml up -d

# From prod to dev
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.dev.yml up -d
```

## Database Operations

```bash
# Backup dev database
docker-compose -f docker-compose.dev.yml exec postgres pg_dump -U crm_dev_user crm_dev > backup_dev.sql

# Backup prod database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U crm_prod_user crm_prod > backup_prod.sql

# Restore to dev
docker-compose -f docker-compose.dev.yml exec -T postgres psql -U crm_dev_user crm_dev < backup.sql

# Restore to prod (CAREFUL!)
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U crm_prod_user crm_prod < backup.sql
```

## Container Access

```bash
# Access dev database
docker-compose -f docker-compose.dev.yml exec postgres psql -U crm_dev_user crm_dev

# Access prod database
docker-compose -f docker-compose.prod.yml exec postgres psql -U crm_prod_user crm_prod

# Access dev API shell
docker-compose -f docker-compose.dev.yml exec api python

# Access prod API shell (CAREFUL!)
docker-compose -f docker-compose.prod.yml exec api python
```

## Creating Admin Users

```bash
# Create admin in dev
docker-compose -f docker-compose.dev.yml exec api python -m scripts.create_admin

# Create admin in prod
docker-compose -f docker-compose.prod.yml exec api python -m scripts.create_admin
```

## File Locations

- **Dev Config**: `docker-compose.dev.yml`
- **Prod Config**: `docker-compose.prod.yml`
- **Current Config**: `docker-compose.yml` (legacy, essentially dev)
- **Dev Env**: `.env` (active development)
- **Prod Env**: `.env.production` (create from template)
- **Dev Template**: `.env.dev.example`
- **Prod Template**: `.env.production.example`

## URLs

### Development
- Web: http://localhost
- API: http://localhost/api
- API Docs: http://localhost/api/docs

### Production
- Web: https://krc.bakersfieldesports.com (or your domain)
- API: https://krc.bakersfieldesports.com/api
- API Docs: https://krc.bakersfieldesports.com/api/docs

## Common Issues

**"Port 80 already in use"**
```bash
# Stop the current environment first
docker-compose down
# Or
docker-compose -f docker-compose.dev.yml down
```

**"Can't connect to database"**
```bash
# Check if postgres is healthy
docker-compose -f docker-compose.dev.yml ps
# View postgres logs
docker-compose -f docker-compose.dev.yml logs postgres
```

**"Need to start fresh"**
```bash
# Remove all dev data
docker-compose -f docker-compose.dev.yml down
docker volume rm crm_postgres_data_dev crm_redis_data_dev
docker-compose -f docker-compose.dev.yml up -d
```
