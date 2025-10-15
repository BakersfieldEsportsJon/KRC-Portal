# Production Deployment Instructions

## ✅ Pre-Deployment Checklist Completed

### 1. Service Health Issues - FIXED ✓
- ✅ Scheduler service: Fixed command to use `rqscheduler`
- ✅ Web service: Added `wget` to nginx container for health checks
- ✅ Removed obsolete `version` field from docker-compose.yml

### 2. Production Secrets - GENERATED ✓
All secrets have been generated and stored in `.env.production`:
- ✅ SECRET_KEY (64-char hex)
- ✅ JWT_SECRET_KEY (64-char hex)
- ✅ ZAPIER_HMAC_SECRET (base64)

### 3. Environment Configuration - READY ✓
- ✅ Created `.env.production` with production settings
- ✅ CORS configured for production domains
- ✅ APP_ENV set to production

---

## 🚀 Deployment Steps

### Step 1: Prepare Production Server

```bash
# 1. Install Docker and Docker Compose
sudo apt update
sudo apt install docker.io docker-compose -y

# 2. Clone or copy the repository to production server
git clone <your-repo> /opt/CRM
# OR copy files via scp/rsync

cd /opt/CRM
```

### Step 2: Configure Environment

```bash
# 1. Copy production environment file
cp .env.production .env

# 2. Edit .env and update these values:
nano .env
```

**Required Updates in `.env`:**
```bash
# Update database password
DATABASE_URL=postgresql://crm_user:CHANGE_THIS_PASSWORD@postgres:5432/crm_db

# Update Zapier webhook (if using messaging)
ZAPIER_CATCH_HOOK_URL=https://hooks.zapier.com/hooks/catch/YOUR_ACTUAL_HOOK_ID/

# Update ggLeap API key (if using gaming center integration)
GGLEAP_API_KEY=YOUR_ACTUAL_GGLEAP_API_KEY
```

### Step 3: Configure DNS

Point these domains to your production server IP:
- `krc.bakersfieldesports.com` → Server IP
- `kiosk.bakersfieldesports.com` → Server IP

Verify DNS propagation:
```bash
dig krc.bakersfieldesports.com
dig kiosk.bakersfieldesports.com
```

### Step 4: Deploy Services

```bash
# 1. Build and start all services
docker compose up -d

# 2. Wait for services to be healthy (check every 10 seconds)
watch docker compose ps

# 3. Check logs for errors
docker compose logs -f
```

### Step 5: Run Database Migrations

```bash
# Run Alembic migrations
docker compose exec api alembic upgrade head
```

### Step 6: Setup Production Admin Account

```bash
# Run the user setup script
docker compose exec api python /app/scripts/setup_production_users.py
```

Follow the prompts to:
1. Create a new admin account with a strong password (min 12 chars, uppercase, lowercase, digits, special chars)
2. Disable or delete demo accounts

**Important**:
- Save the admin credentials securely!
- New users can also be created via the Admin UI with temporary passwords
- Users created by admin will be forced to change their password on first login

### Step 7: Verify Deployment

#### Check Service Health
```bash
# All services should show "healthy" or "Up"
docker compose ps

# Check API health endpoint
curl https://krc.bakersfieldesports.com/api/v1/healthz
```

#### Test Access
1. Visit `https://krc.bakersfieldesports.com`
2. Visit `https://kiosk.bakersfieldesports.com`
3. Verify SSL certificates are valid (no warnings)

#### Test Admin Login
1. Go to `https://krc.bakersfieldesports.com`
2. Login with your new admin credentials
3. Verify you can access all admin features
4. Test creating a new staff user with a temporary password

#### Test Staff Account (Password Change Flow)
If you created a staff account with a temporary password:
1. Login as staff with temporary password
2. Verify you are automatically redirected to change password page
3. Set a new strong password meeting all requirements
4. Verify you can then access the system normally
5. Verify staff can:
   - ✓ View clients
   - ✓ Edit notes only
   - ✗ Cannot create/delete clients (should get 403 error)

#### Test Kiosk
1. Go to `https://kiosk.bakersfieldesports.com`
2. Test phone number lookup
3. Test check-in process

---

## 🔒 Security Verification

### SSL/TLS
- [ ] HTTPS works for both domains
- [ ] SSL certificates are valid
- [ ] HTTP redirects to HTTPS

### Authentication
- [ ] Demo accounts disabled/deleted
- [ ] Admin account created with strong password
- [ ] Password change flow tested (forced password change on first login)
- [ ] Strong password requirements enforced (12+ chars, complexity)
- [ ] JWT tokens working correctly
- [ ] Sessions expire after configured time

### Authorization
- [ ] Staff cannot access admin-only endpoints
- [ ] API returns 403 for unauthorized actions
- [ ] CORS only allows production domains

### Secrets
- [ ] `.env` file contains production secrets
- [ ] `.env` is NOT committed to git (check .gitignore)
- [ ] Secrets stored securely (consider secrets manager)

---

## 📊 Post-Deployment Monitoring

### First Hour
```bash
# Watch logs continuously
docker compose logs -f

# Check for errors
docker compose logs | grep -i error

# Monitor resource usage
docker stats
```

### Daily Checks (First Week)
```bash
# Service health
docker compose ps

# Disk space
df -h

# Recent errors
docker compose logs --since 24h | grep -i error

# Database size
docker compose exec postgres psql -U crm_user -d crm_db -c "SELECT pg_size_pretty(pg_database_size('crm_db'));"
```

---

## 🔄 Backup Strategy

### Manual Backup
```bash
# Create backup
docker compose exec postgres pg_dump -U crm_user crm_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Automated Daily Backups
Add to crontab:
```bash
# Open crontab
crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * cd /opt/CRM && docker compose exec -T postgres pg_dump -U crm_user crm_db | gzip > /opt/backups/crm_$(date +\%Y\%m\%d).sql.gz
```

### Test Restore
```bash
# Test restoring from backup
gunzip -c backup_20251014.sql.gz | docker compose exec -T postgres psql -U crm_user crm_db
```

---

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check logs for errors
docker compose logs

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database Connection Issues
```bash
# Test database connection
docker compose exec api python -c "from core.database import engine; import asyncio; asyncio.run(engine.connect())"

# Check DATABASE_URL in .env
docker compose exec api env | grep DATABASE_URL
```

### SSL Not Working
- Verify ports 80 and 443 are open
- Check DNS is pointing to correct IP
- Check Caddy logs: `docker compose logs caddy`
- Verify Caddyfile is configured correctly

### Login Issues
- Check JWT_SECRET_KEY matches in .env
- Verify user exists: Run user setup script (option 4 to list users)
- Check API logs: `docker compose logs api | grep -i auth`

---

## 📞 Support

### Useful Commands
```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs api
docker compose logs web
docker compose logs scheduler

# Restart specific service
docker compose restart api

# Access database shell
docker compose exec postgres psql -U crm_user -d crm_db

# Access API container shell
docker compose exec api bash
```

### Service Status
- **API**: http://localhost:8000/docs (internal only)
- **Health Check**: https://krc.bakersfieldesports.com/api/v1/healthz
- **Admin UI**: https://krc.bakersfieldesports.com
- **Kiosk UI**: https://kiosk.bakersfieldesports.com

---

## ✅ Success Criteria

Deployment is successful when:
- [x] All Docker services are healthy
- [ ] HTTPS works for both domains
- [ ] Admin can login and perform all functions
- [ ] Staff can view/edit notes only
- [ ] Kiosk check-in works
- [ ] No errors in logs for 1 hour
- [ ] Database backups working
- [ ] Demo accounts removed/disabled

---

**Deployment Date**: _________________
**Deployed By**: _________________
**Admin Email**: _________________
**Notes**: _________________
