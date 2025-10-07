# Production Deployment Checklist

## 🚨 Critical - Must Complete Before Production

### 1. Database & Migrations
- [x] ✅ Database migration for `notes` and `language` fields created and tested
- [ ] ⚠️ Review all migration files for safety (no DROP TABLE commands)
- [ ] Run all migrations on production database
- [ ] Create initial database backup
- [ ] Test backup restoration process

### 2. Security & Authentication
- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Generate strong JWT_SECRET_KEY: `openssl rand -hex 32`
- [ ] Change all default passwords in database
- [ ] Remove or disable test/demo user accounts
- [ ] Verify all API endpoints require authentication
- [x] ✅ Role-based access controls implemented (Admin/Staff)
- [ ] Test role-based permissions thoroughly

### 3. Environment Configuration
- [ ] Set `APP_ENV=production` in `.env`
- [ ] Update `CORS_ORIGINS` to production domains only
- [ ] Configure production database URL
- [ ] Configure Redis URL
- [ ] Set proper timezone (`TZ=America/Los_Angeles`)
- [ ] Configure Zapier webhook URL and HMAC secret
- [ ] Configure ggLeap API key (if using)
- [ ] Set `ZAPIER_MODE=production`

### 4. Domain & SSL
- [ ] DNS records pointing to server:
  - `krc.bakersfieldesports.com` → Server IP
  - `kiosk.bakersfieldesports.com` → Server IP
- [ ] Ports 80 and 443 open on server
- [ ] Verify Caddy auto-SSL works
- [ ] Test HTTPS redirects
- [ ] Verify SSL certificates issued correctly

### 5. Backend API Protection
- [x] ✅ Admin-only endpoints protected
- [x] ✅ Staff-only access to notes field
- [ ] Add rate limiting (recommended)
- [ ] Test all protected endpoints
- [ ] Verify 403 errors for unauthorized access

---

## ⚠️ Important - Should Complete

### 6. Monitoring & Logging
- [ ] Configure log rotation for Caddy logs
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor disk space
- [ ] Set up health check monitoring
- [ ] Configure alerts for service failures

### 7. Backup Strategy
- [ ] Test automated backups: `make backup`
- [ ] Schedule daily backups via cron:
  ```bash
  0 2 * * * cd /path/to/CRM && make backup
  ```
- [ ] Test restore process
- [ ] Configure backup retention policy
- [ ] Store backups off-server

### 8. Performance
- [x] ✅ Database connection pooling configured
- [ ] Redis caching enabled
- [ ] Database indexes optimized
- [ ] Static assets optimized
- [ ] Gzip compression enabled (via Caddy)

### 9. Frontend Build
- [ ] Build production frontend: `cd apps/web && npm run build`
- [ ] Verify production build works
- [ ] Test on production domains
- [ ] Verify API calls work from production domains

---

## 📝 Pre-Deployment Testing

### Test Admin User
- [ ] Login as admin
- [ ] Create new client
- [ ] Edit all client fields
- [ ] Delete client
- [ ] Add/remove tags
- [ ] Create membership
- [ ] Check in client

### Test Staff User
- [ ] Login as staff
- [ ] View client list
- [ ] View client details
- [ ] Edit client notes (should work)
- [ ] Try to edit other fields (should fail with 403)
- [ ] Try to create client (should fail with 403)
- [ ] Try to delete client (should fail with 403)
- [ ] Check in client (should work)

### Test Kiosk
- [ ] Phone number lookup works
- [ ] Check-in process completes
- [ ] Check-in appears in database
- [ ] Error handling works (wrong phone, etc.)

### Test Integrations
- [ ] Zapier webhook sends successfully
- [ ] Zapier HMAC signature validates
- [ ] ggLeap sync works (if enabled)
- [ ] SMS messages send (if enabled)

---

## 🚀 Deployment Steps

### Step 1: Prepare Server
```bash
# Install Docker and Docker Compose on server
sudo apt update
sudo apt install docker.io docker-compose

# Clone repository
git clone <repository-url> /opt/CRM
cd /opt/CRM
```

### Step 2: Configure Environment
```bash
# Copy and edit production environment file
cp .env.example .env
nano .env

# Update these critical values:
# - APP_ENV=production
# - SECRET_KEY=<generate-with-openssl>
# - JWT_SECRET_KEY=<generate-with-openssl>
# - DATABASE_URL=<production-db-url>
# - CORS_ORIGINS=https://krc.bakersfieldesports.com,https://kiosk.bakersfieldesports.com
# - ZAPIER_CATCH_HOOK_URL=<your-zapier-url>
# - ZAPIER_HMAC_SECRET=<your-hmac-secret>
```

### Step 3: Deploy
```bash
# Build and start services
docker compose up -d

# Run migrations
docker compose exec api alembic upgrade head

# Verify services are healthy
docker compose ps
docker compose logs -f api
```

### Step 4: Create Admin User
```bash
# Access API container
docker compose exec api python

# In Python shell:
from apps.api.models import User
from modules.core_auth.utils import hash_password
from core.database import SessionLocal

db = SessionLocal()
admin = User(
    email="admin@bakersfieldesports.com",
    password_hash=hash_password("SECURE_PASSWORD_HERE"),
    role="admin",
    is_active=True
)
db.add(admin)
db.commit()
exit()
```

### Step 5: Verify Deployment
- [ ] Visit https://krc.bakersfieldesports.com
- [ ] Visit https://kiosk.bakersfieldesports.com
- [ ] Check SSL certificates
- [ ] Login as admin
- [ ] Test core functionality

---

## 🔍 Post-Deployment Verification

### Immediate Checks (First Hour)
- [ ] All services running: `docker compose ps`
- [ ] No errors in logs: `docker compose logs`
- [ ] Database accessible
- [ ] Redis accessible
- [ ] API responding: `curl https://krc.bakersfieldesports.com/api/v1/healthz`
- [ ] Admin can login
- [ ] Staff can login
- [ ] Kiosk works

### First Day Checks
- [ ] Monitor error logs
- [ ] Check disk space
- [ ] Verify backups running
- [ ] Test all user workflows
- [ ] Monitor performance

### First Week Checks
- [ ] Review backup retention
- [ ] Check log file sizes
- [ ] Monitor database growth
- [ ] Review security logs
- [ ] Get user feedback

---

## 🆘 Rollback Plan

If issues occur during deployment:

```bash
# Stop services
docker compose down

# Restore from backup (if database changes were made)
docker compose exec postgres psql -U crm_user -d crm_db < backup.sql

# Revert to previous version
git checkout <previous-commit>
docker compose up -d
```

---

## 📞 Support Contacts

**Technical Issues:**
- Review logs: `docker compose logs -f`
- Check health: `docker compose ps`
- API docs: https://krc.bakersfieldesports.com/api/v1/docs

**Common Issues:**
- **Services won't start**: Check logs, verify .env file
- **Database connection errors**: Verify DATABASE_URL
- **SSL not working**: Check DNS, verify ports 80/443 open
- **Login fails**: Check JWT_SECRET_KEY matches

---

## 📊 Success Criteria

Deployment is successful when:
- [x] All Docker services are healthy
- [ ] HTTPS works for both domains
- [ ] Admin can perform all functions
- [ ] Staff can view and add notes only
- [ ] Kiosk check-in works
- [ ] No errors in logs for 1 hour
- [ ] Database backups working
- [ ] All tests pass

---

**Last Updated:** 2025-10-03
**Version:** 1.0.0
