# Environment Setup Guide

This guide explains how to set up and manage separate development and production environments for the KRC Gaming Center CRM.

## Overview

The project now supports two completely separate environments:

- **Development Environment**: For testing and development with test data
- **Production Environment**: For live operations with real customer data

Each environment has:
- Its own database (completely separate data)
- Its own Docker Compose configuration
- Its own environment variables file
- Separate Docker volumes (no data mixing)

## Quick Start

### Development Environment

1. **Create development environment file**:
   ```bash
   cp .env.dev.example .env
   ```

2. **Start development environment**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Check status**:
   ```bash
   docker-compose -f docker-compose.dev.yml ps
   ```

4. **View logs**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

5. **Stop development environment**:
   ```bash
   docker-compose -f docker-compose.dev.yml down
   ```

### Production Environment

1. **Create production environment file**:
   ```bash
   cp .env.production.example .env.production
   ```

2. **Edit `.env.production` and update all values**:
   - Change `SECRET_KEY` to a strong random value
   - Change `JWT_SECRET_KEY` to a strong random value
   - Set strong `POSTGRES_PASSWORD`
   - Update `DATABASE_URL` with the new password
   - Configure real API keys (Zapier, ggLeap, etc.)
   - Set production hostnames

3. **Start production environment**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Check status**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

5. **View logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

6. **Stop production environment**:
   ```bash
   docker-compose -f docker-compose.prod.yml down
   ```

## Key Differences Between Environments

### Development Environment
- **Database**: `crm_dev` with user `crm_dev_user`
- **Docker Volumes**: `postgres_data_dev`, `redis_data_dev`, etc.
- **Features**: External integrations disabled (ggLeap sync off)
- **Security**: Uses weak passwords (acceptable for local dev)
- **Zapier**: Runs in `dev_log` mode (logs instead of sending)
- **CORS**: Allows localhost origins
- **Data**: Test/development data only

### Production Environment
- **Database**: `crm_prod` with user `crm_prod_user`
- **Docker Volumes**: `postgres_data_prod`, `redis_data_prod`, etc.
- **Features**: All integrations enabled
- **Security**: Requires strong passwords and secrets
- **Zapier**: Runs in `production` mode (actually sends webhooks)
- **CORS**: Restricted to production domains
- **Data**: Real customer data

## Running Both Environments Simultaneously

You CAN run both environments at the same time if needed, but you'll need to modify port mappings to avoid conflicts:

### Option 1: Use the current docker-compose.yml as-is
The current `docker-compose.yml` is essentially the development config. You can:
```bash
# Run dev with current file
docker-compose up -d

# Run prod with dedicated file (won't conflict)
docker-compose -f docker-compose.prod.yml up -d
```

Note: Both will try to use ports 80 and 443. You'll need to stop one to start the other, OR modify one to use different ports.

### Option 2: Modify ports for one environment
Edit `docker-compose.dev.yml` to use different ports:
```yaml
caddy:
  ports:
    - "8080:80"    # Dev on port 8080
    - "8443:443"   # Dev on port 8443
```

Then you can run both simultaneously:
- Development: http://localhost:8080
- Production: http://localhost (port 80)

## Managing Data

### Backing Up Development Data
```bash
# Backup development database
docker-compose -f docker-compose.dev.yml exec postgres pg_dump -U crm_dev_user crm_dev > backup_dev.sql
```

### Backing Up Production Data
```bash
# Backup production database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U crm_prod_user crm_prod > backup_prod.sql
```

### Resetting Development Data
If you want to start fresh with development:
```bash
# Stop dev environment
docker-compose -f docker-compose.dev.yml down

# Remove dev volumes (THIS DELETES ALL DEV DATA!)
docker volume rm crm_postgres_data_dev crm_redis_data_dev

# Start fresh
docker-compose -f docker-compose.dev.yml up -d
```

### Importing Test Data to Development
```bash
# Import SQL file to development database
docker-compose -f docker-compose.dev.yml exec -T postgres psql -U crm_dev_user crm_dev < test_data.sql
```

## Switching Between Environments

### Currently Running Development, Want to Test Production:
```bash
# Stop dev
docker-compose -f docker-compose.dev.yml down

# Start prod
docker-compose -f docker-compose.prod.yml up -d
```

### Currently Running Production, Want to Develop:
```bash
# Stop prod (CAREFUL - make sure you want to stop production!)
docker-compose -f docker-compose.prod.yml down

# Start dev
docker-compose -f docker-compose.dev.yml up -d
```

## Creating Initial Admin User

### For Development:
```bash
docker-compose -f docker-compose.dev.yml exec api python -m scripts.create_admin
```

### For Production:
```bash
docker-compose -f docker-compose.prod.yml exec api python -m scripts.create_admin
```

## Rebuilding Containers

### Development:
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

### Production:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Viewing Container Logs

### Development:
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f api
```

### Production:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api
```

## Security Best Practices

### Development Environment
- ✅ Can use simple passwords (it's local)
- ✅ Can commit .env file (with dev credentials)
- ✅ External integrations should be disabled
- ✅ Test data only

### Production Environment
- ❌ **NEVER** commit `.env.production` to git
- ✅ Use strong, randomly generated passwords
- ✅ Store secrets securely (password manager, secrets manager)
- ✅ Enable all security features
- ✅ Regular backups of production data
- ✅ Monitor logs for suspicious activity

## Troubleshooting

### "Port already in use" error
Another service is using ports 80/443. Either:
1. Stop the other service
2. Change ports in docker-compose file
3. Make sure you stopped the other environment first

### "Volume already in use" error
You're trying to use the same volume name. Make sure the volume names are different (dev vs prod).

### Database connection failed
Check:
1. `.env` file has correct credentials
2. `DATABASE_URL` matches `POSTGRES_PASSWORD`
3. Container is healthy: `docker-compose ps`

### Container won't start
Check logs:
```bash
docker-compose -f docker-compose.dev.yml logs <service-name>
```

## File Reference

- `docker-compose.dev.yml` - Development environment configuration
- `docker-compose.prod.yml` - Production environment configuration
- `docker-compose.yml` - Current/legacy file (can be used as-is for dev)
- `.env` - Development environment variables (active)
- `.env.production` - Production environment variables (create from template)
- `.env.dev.example` - Development environment template
- `.env.production.example` - Production environment template

## Next Steps

After setting up your environments:

1. **Test Development**: Create test users and clients in dev environment
2. **Populate Test Data**: Import or create sample data for testing
3. **Configure Production**: Set up `.env.production` with real values
4. **Test Production**: Deploy to production and test with one real user
5. **Monitor**: Watch logs and monitor both environments
6. **Backup Strategy**: Set up automated backups for production

## Questions?

Refer to:
- `DEPLOYMENT_INSTRUCTIONS.md` - General deployment guide
- `PROJECT_STATUS.md` - Current project status
- `docs/` - Detailed documentation
