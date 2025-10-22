# Update Strategy - Protecting Production Data

## Overview

This guide ensures your production database stays safe during software updates.

## Key Principle: Docker Volumes Persist

**Good News:** Docker volumes are **NEVER** deleted during updates unless you explicitly delete them.

When you run `docker-compose up -d --build`, Docker will:
- ✅ Rebuild application containers (API, web, worker)
- ✅ Restart containers with new code
- ❌ **NOT** touch your database volumes
- ❌ **NOT** delete any data

## Safe Update Process

### For Development Environment

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild and restart (data is safe)
docker-compose -f docker-compose.dev.yml up -d --build

# 3. Check everything is running
docker-compose -f docker-compose.dev.yml ps
```

**Dev data is preserved** in `crm_postgres_data_dev` volume.

### For Production Environment

```bash
# 1. BACKUP FIRST (always!)
./scripts/backup-production.sh
# OR manually:
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U crm_prod_user crm_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull latest code
git pull origin main

# 3. Rebuild and restart (data is safe)
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Verify
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs api --tail 50

# 5. Test critical functionality
curl http://localhost/api/v1/healthz
```

**Production data is preserved** in `crm_postgres_data_prod` volume.

## What Gets Updated vs What Stays

### Updated (Rebuilt):
- ✅ API code (FastAPI application)
- ✅ Web frontend (React application)
- ✅ Worker code (background jobs)
- ✅ Application logic
- ✅ Dependencies (Python packages, npm packages)

### NOT Updated (Persists):
- ✅ Database data (all customer/client records)
- ✅ Database tables and schemas
- ✅ Redis data (session/cache data)
- ✅ Caddy SSL certificates
- ✅ Environment variables (`.env` files)

## Commands That ARE Safe

These commands will **NOT** delete data:

```bash
# Safe - rebuilds code, keeps data
docker-compose -f docker-compose.prod.yml up -d --build

# Safe - just restarts containers
docker-compose -f docker-compose.prod.yml restart

# Safe - stops containers, data remains
docker-compose -f docker-compose.prod.yml down

# Safe - starts stopped containers
docker-compose -f docker-compose.prod.yml up -d

# Safe - rebuilds specific service
docker-compose -f docker-compose.prod.yml up -d --build api
```

## Commands That DELETE Data (DANGEROUS!)

**⚠️ NEVER run these on production without a backup:**

```bash
# DANGEROUS - Deletes volumes (all data lost!)
docker-compose -f docker-compose.prod.yml down -v

# DANGEROUS - Manually deletes production data
docker volume rm crm_postgres_data_prod

# DANGEROUS - Deletes all volumes
docker volume prune
```

## Database Schema Updates (Migrations)

If your update includes database schema changes (new tables, columns, etc.):

### Option 1: Using Alembic (Recommended)

```bash
# 1. Backup first
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U crm_prod_user crm_prod > backup_before_migration.sql

# 2. Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 3. Verify
docker-compose -f docker-compose.prod.yml exec postgres psql -U crm_prod_user -d crm_prod -c "\dt"
```

### Option 2: Manual SQL (if needed)

```bash
# Apply schema changes manually
docker-compose -f docker-compose.prod.yml exec postgres psql -U crm_prod_user -d crm_prod < migration.sql
```

## Backup Strategy

### Automated Backup Script

Create `scripts/backup-production.sh`:

```bash
#!/bin/bash
# Backup production database

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/prod_backup_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Backup database
docker-compose -f docker-compose.prod.yml exec -T postgres \
    pg_dump -U crm_prod_user crm_prod > ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}

echo "Backup created: ${BACKUP_FILE}.gz"

# Keep only last 30 days of backups
find ${BACKUP_DIR} -name "prod_backup_*.sql.gz" -mtime +30 -delete
```

Make it executable:
```bash
chmod +x scripts/backup-production.sh
```

### Manual Backup (Quick)

```bash
# Production
docker-compose -f docker-compose.prod.yml exec postgres \
    pg_dump -U crm_prod_user crm_prod > backup_prod.sql

# Development
docker-compose -f docker-compose.dev.yml exec postgres \
    pg_dump -U crm_dev_user crm_dev > backup_dev.sql
```

### Restore from Backup

```bash
# Production
docker-compose -f docker-compose.prod.yml exec -T postgres \
    psql -U crm_prod_user crm_prod < backup_prod.sql

# Development
docker-compose -f docker-compose.dev.yml exec -T postgres \
    psql -U crm_dev_user crm_dev < backup_dev.sql
```

## Testing Updates Safely

### 1. Test in Development First

```bash
# Update dev environment
git pull
docker-compose -f docker-compose.dev.yml up -d --build

# Test thoroughly
# - Login
# - Create/edit clients
# - Check reports
# - Test all features
```

### 2. Clone Production Data to Dev for Testing

```bash
# 1. Backup production
docker-compose -f docker-compose.prod.yml exec postgres \
    pg_dump -U crm_prod_user crm_prod > prod_data.sql

# 2. Stop dev
docker-compose -f docker-compose.dev.yml down

# 3. Clear dev database
docker volume rm crm_postgres_data_dev

# 4. Start dev
docker-compose -f docker-compose.dev.yml up -d

# 5. Wait for database to be ready
sleep 10

# 6. Restore production data to dev
docker-compose -f docker-compose.dev.yml exec -T postgres \
    psql -U crm_dev_user crm_dev < prod_data.sql

# 7. Test update with real data
docker-compose -f docker-compose.dev.yml up -d --build
```

### 3. Update Production (After Testing)

```bash
# 1. Backup
./scripts/backup-production.sh

# 2. Update
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f api

# 4. Verify health
curl http://localhost/api/v1/healthz
```

## Rollback Plan

If an update breaks something:

### Rollback Code

```bash
# 1. Stop containers
docker-compose -f docker-compose.prod.yml down

# 2. Revert code
git log --oneline  # Find the commit to revert to
git checkout <previous-commit-hash>

# 3. Rebuild with old code
docker-compose -f docker-compose.prod.yml up -d --build
```

### Rollback Database (if schema changed)

```bash
# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T postgres \
    psql -U crm_prod_user crm_prod < backup_before_update.sql
```

## Update Checklist

Before each production update:

- [ ] Backup production database
- [ ] Test update in development environment
- [ ] Review git changes (`git diff` or `git log`)
- [ ] Check for database schema changes
- [ ] Plan maintenance window (if needed)
- [ ] Notify users (if downtime expected)
- [ ] Have rollback plan ready
- [ ] Monitor logs after update
- [ ] Test critical features after update

## Common Update Scenarios

### Scenario 1: Bug Fix (No DB Changes)

```bash
# Quick update - 1-2 minutes downtime
docker-compose -f docker-compose.prod.yml up -d --build
```

### Scenario 2: New Feature (With DB Schema Changes)

```bash
# 1. Backup
./scripts/backup-production.sh

# 2. Pull code
git pull

# 3. Run migrations
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 4. Verify
docker-compose -f docker-compose.prod.yml logs api --tail 50
```

### Scenario 3: Major Update (Multiple Services)

```bash
# 1. Backup everything
./scripts/backup-production.sh

# 2. Update code
git pull

# 3. Rebuild all services
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Verify each service
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail 50

# 5. Test functionality
```

## Monitoring After Updates

```bash
# Watch logs in real-time
docker-compose -f docker-compose.prod.yml logs -f

# Check for errors
docker-compose -f docker-compose.prod.yml logs api | grep ERROR

# Verify database connections
docker-compose -f docker-compose.prod.yml logs api | grep "Database"

# Check container health
docker-compose -f docker-compose.prod.yml ps
```

## Emergency Recovery

If something goes catastrophically wrong:

```bash
# 1. Stop everything
docker-compose -f docker-compose.prod.yml down

# 2. Revert code to last known good version
git checkout <last-working-commit>

# 3. Restore database backup
docker-compose -f docker-compose.prod.yml up -d postgres
sleep 10
docker-compose -f docker-compose.prod.yml exec -T postgres \
    psql -U crm_prod_user crm_prod < last_good_backup.sql

# 4. Restart with old code
docker-compose -f docker-compose.prod.yml up -d --build
```

## Summary

**Remember:**
- Docker volumes **persist** across updates by default
- Always backup before production updates
- Test in dev first
- Database data is **NEVER** touched by `docker-compose up -d --build`
- Only explicit volume deletion commands can remove data
- When in doubt, backup first!

**The Golden Rule:** If you don't run `docker volume rm` or `docker-compose down -v`, your data is safe.
