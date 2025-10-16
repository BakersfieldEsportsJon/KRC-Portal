# Synology NAS Installation Guide

## BEC CRM System - Docker Deployment on Synology NAS

**Version:** 1.0
**Last Updated:** October 2025
**Target Environment:** Synology NAS with Docker support

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Synology NAS Preparation](#synology-nas-preparation)
3. [Installation Steps](#installation-steps)
4. [Initial Configuration](#initial-configuration)
5. [First-Time Setup](#first-time-setup)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Synology NAS Requirements

- **Model:** Any Synology NAS with Docker support (DS218+, DS920+, DS1522+, etc.)
- **DSM Version:** DSM 7.0 or higher
- **RAM:** Minimum 4GB (8GB+ recommended)
- **Storage:** Minimum 20GB free space for application and database
- **CPU:** x86-64 processor (Intel/AMD)

### Network Requirements

- **Static IP Address:** Recommended for the NAS on your local network
- **Port Access:** Ability to access ports 80 and 443 (or alternative ports)
- **Domain Names (Optional but Recommended):**
  - `krc.bakersfieldesports.com` → Admin interface
  - `kiosk.bakersfieldesports.com` → Kiosk interface

### Required Knowledge

- Basic familiarity with Synology DSM interface
- Basic understanding of Docker concepts
- Ability to use SSH (for advanced configuration)

---

## Synology NAS Preparation

### Step 1: Install Required Packages

1. Open **Package Center** on your Synology DSM
2. Search for and install:
   - **Docker** (Container Manager in DSM 7.2+)
   - **Text Editor** (optional, for editing config files)
   - **Git Server** (optional, for version control)

### Step 2: Enable SSH Access (Recommended)

1. Go to **Control Panel** → **Terminal & SNMP**
2. Check **Enable SSH service**
3. Set port to **22** (default) or custom port
4. Click **Apply**

### Step 3: Create Project Directory

#### Option A: Using File Station (GUI)

1. Open **File Station**
2. Navigate to a shared folder (e.g., `docker`)
3. Create new folder: `bec-crm`
4. Inside `bec-crm`, create folders:
   - `data` (for database persistence)
   - `redis` (for Redis persistence)
   - `backups` (for database backups)

#### Option B: Using SSH (Advanced)

```bash
# SSH into your Synology
ssh admin@your-nas-ip

# Create directory structure
sudo mkdir -p /volume1/docker/bec-crm/{data,redis,backups}
sudo chown -R $USER:users /volume1/docker/bec-crm
```

---

## Installation Steps

### Step 1: Upload Project Files to NAS

#### Option A: Using File Station

1. Download the project ZIP from your repository
2. Open **File Station** on Synology
3. Navigate to `/docker/bec-crm`
4. Click **Upload** and select all project files
5. Extract if uploaded as ZIP

#### Option B: Using Git (Recommended)

```bash
# SSH into Synology
ssh admin@your-nas-ip

# Navigate to docker folder
cd /volume1/docker/bec-crm

# Clone repository (if using Git)
git clone <your-repo-url> .

# Or upload files via SCP from your computer
scp -r /path/to/CRM/* admin@your-nas-ip:/volume1/docker/bec-crm/
```

### Step 2: Configure Environment Variables

1. Navigate to `/volume1/docker/bec-crm`
2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Edit `.env` file with Text Editor or via SSH:

```bash
nano .env
```

4. Update the following critical settings:

```bash
# Application
APP_ENV=production
SECRET_KEY=CHANGE_THIS_TO_RANDOM_STRING_MIN_32_CHARS
TZ=America/Los_Angeles

# Database
POSTGRES_PASSWORD=CHANGE_THIS_TO_SECURE_PASSWORD
DATABASE_URL=postgresql://crm_user:SAME_PASSWORD_HERE@postgres:5432/crm_db

# Redis
REDIS_URL=redis://redis:6379/0

# Authentication
JWT_SECRET_KEY=CHANGE_THIS_TO_ANOTHER_RANDOM_STRING
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (adjust based on your access method)
CORS_ORIGINS=http://YOUR_NAS_IP:5173,http://YOUR_NAS_IP:8000

# Zapier Integration (configure later if needed)
ZAPIER_CATCH_HOOK_URL=https://hooks.zapier.com/hooks/catch/your-hook-id/
ZAPIER_HMAC_SECRET=your-zapier-hmac-secret
ZAPIER_MODE=test

# Textla Messaging
TEXTLA_SENDER=+18668849961

# Feature Flags
FEATURE_MESSAGING=false
FEATURE_GGLEAP_SYNC=false
```

**Important Security Notes:**
- Replace all `CHANGE_THIS_*` values with strong random strings
- Generate secure secrets using: `openssl rand -hex 32`
- Keep this file secure - it contains sensitive credentials

### Step 3: Update Docker Compose for Synology

Edit `docker-compose.yml` to use proper volume paths for Synology:

```bash
nano docker-compose.yml
```

Update volume mappings to use absolute paths:

```yaml
volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /volume1/docker/bec-crm/data

  redis-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /volume1/docker/bec-crm/redis
```

### Step 4: Deploy with Docker Compose

#### Option A: Using Container Manager (DSM 7.2+)

1. Open **Container Manager** (or **Docker** in older DSM)
2. Click **Project**
3. Click **Create**
4. Set **Project Name:** `bec-crm`
5. Set **Path:** `/docker/bec-crm`
6. Set **Source:** `docker-compose.yml`
7. Click **Next**
8. Review configuration
9. Click **Done**

The system will download images and start containers.

#### Option B: Using SSH Command Line

```bash
# Navigate to project directory
cd /volume1/docker/bec-crm

# Start the stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Run Database Migrations

```bash
# SSH into NAS
ssh admin@your-nas-ip

# Navigate to project
cd /volume1/docker/bec-crm

# Run migrations
docker-compose exec api alembic upgrade head
```

### Step 6: Seed Initial Data

```bash
# Create admin user and demo data
docker-compose exec api python scripts/seed.py
```

This creates:
- **Admin user:** `admin@bakersfieldesports.com` / temporary password (you'll be prompted to change on first login)
- Demo clients and memberships (optional)

---

## Initial Configuration

### Configure Port Access

#### Option A: Access via NAS IP and Ports

Access the applications directly:
- **Admin Interface:** `http://YOUR_NAS_IP:5173`
- **Kiosk Interface:** `http://YOUR_NAS_IP:5173/kiosk`
- **API Docs:** `http://YOUR_NAS_IP:8000/docs`

#### Option B: Configure Reverse Proxy (Recommended for Production)

1. Go to **Control Panel** → **Login Portal** → **Advanced** → **Reverse Proxy**
2. Click **Create**

**For Admin Interface:**
- Description: `BEC CRM Admin`
- Source Protocol: `HTTPS`
- Source Hostname: `krc.bakersfieldesports.com` (or your domain)
- Source Port: `443`
- Destination Protocol: `HTTP`
- Destination Hostname: `localhost`
- Destination Port: `5173`

**For Kiosk Interface:**
- Description: `BEC CRM Kiosk`
- Source Protocol: `HTTPS`
- Source Hostname: `kiosk.bakersfieldesports.com`
- Source Port: `443`
- Destination Protocol: `HTTP`
- Destination Hostname: `localhost`
- Destination Port: `5173`

**For API:**
- Description: `BEC CRM API`
- Source Protocol: `HTTPS`
- Source Hostname: `api.bakersfieldesports.com`
- Source Port: `443`
- Destination Protocol: `HTTP`
- Destination Hostname: `localhost`
- Destination Port: `8000`

3. Enable **HSTS** and **HTTP/2** in Custom Headers (recommended)

### Configure Firewall (Optional)

1. Go to **Control Panel** → **Security** → **Firewall**
2. Create rules to allow access to:
   - Port 5173 (Web UI) - from local network only
   - Port 8000 (API) - from local network only
   - Port 443 (HTTPS) - if using reverse proxy

---

## First-Time Setup

### Step 1: Access Admin Interface

1. Open browser and navigate to: `http://YOUR_NAS_IP:5173`
2. You should see the BEC CRM login page

### Step 2: Login and Change Admin Password

1. Login with:
   - Email: `admin@bakersfieldesports.com`
   - Password: `admin123` (temporary)

2. You'll be immediately prompted to change your password
3. Set a strong password (minimum 12 characters, uppercase, lowercase, numbers, special characters)

### Step 3: Create Staff Users

1. Navigate to **Admin** → **User Management**
2. Click **Create User**
3. Enter:
   - Email: `staff@bakersfieldesports.com`
   - Role: `Staff`
4. System will generate a temporary password
5. Share the temporary password securely with the staff member
6. Staff must change password on first login

### Step 4: Configure Kiosk

1. Set up a dedicated kiosk computer/tablet at your facility
2. Open browser in **kiosk mode**:
   - Chrome: `chrome --kiosk http://YOUR_NAS_IP:5173/kiosk`
   - Firefox: Press F11 for fullscreen
3. Bookmark the kiosk URL for easy access
4. Consider using browser extensions to prevent users from exiting kiosk mode

### Step 5: Add Clients

1. Navigate to **Clients** page
2. Click **Add Client**
3. Fill in client information:
   - Name
   - Phone (for kiosk check-in)
   - Email (optional)
   - Tags (optional)
4. Click **Save**

### Step 6: Add Memberships

1. Select a client
2. Click **Manage Membership**
3. Enter:
   - Start Date
   - End Date
   - Membership Type
4. Click **Save**

---

## Verification

### Health Check

```bash
# Check all containers are running
docker-compose ps

# Should show:
# - api (healthy)
# - web (healthy)
# - postgres (healthy)
# - redis (healthy)
# - worker (healthy)

# Check API health endpoint
curl http://localhost:8000/api/v1/healthz

# Should return: {"status":"healthy"}
```

### Test Kiosk Check-In

1. Navigate to kiosk interface: `http://YOUR_NAS_IP:5173/kiosk`
2. Enter a client's phone number (10 digits)
3. Verify client appears and can check in
4. Check admin interface to confirm check-in was recorded

### Test Background Jobs

```bash
# Check worker logs
docker-compose logs worker

# Should see periodic job execution
```

---

## Troubleshooting

### Containers Won't Start

**Check Docker logs:**
```bash
docker-compose logs api
docker-compose logs postgres
docker-compose logs web
```

**Common issues:**
- Port conflicts: Change ports in `docker-compose.yml`
- Permission issues: Check folder ownership
- Memory: Ensure NAS has sufficient RAM

### Cannot Access Web Interface

1. **Verify containers are running:**
   ```bash
   docker-compose ps
   ```

2. **Check firewall rules** on Synology

3. **Verify port forwarding** if accessing remotely

4. **Check CORS settings** in `.env`:
   ```bash
   CORS_ORIGINS=http://YOUR_NAS_IP:5173,http://YOUR_NAS_IP:8000
   ```

### Database Connection Errors

1. **Check PostgreSQL is running:**
   ```bash
   docker-compose exec postgres pg_isready
   ```

2. **Verify credentials** in `.env` match

3. **Check database logs:**
   ```bash
   docker-compose logs postgres
   ```

### Kiosk Can't Find Clients

1. **Verify clients exist** in admin interface
2. **Check phone number format** (must be 10 digits, no formatting)
3. **Check API logs:**
   ```bash
   docker-compose logs api | grep "phone lookup"
   ```

### Performance Issues

1. **Check NAS resource usage:**
   - DSM → Resource Monitor
   - Look for CPU, RAM, or disk bottlenecks

2. **Optimize PostgreSQL:**
   - Increase `shared_buffers` if RAM available
   - Add connection pooling if needed

3. **Check disk health:**
   - Storage Manager → HDD/SSD health

### Backup and Recovery Issues

See `BACKUP_AND_MAINTENANCE.md` for detailed procedures.

---

## Post-Installation Tasks

### Set Up Automated Backups

Configure daily backups using Synology Task Scheduler:

1. **Control Panel** → **Task Scheduler**
2. **Create** → **Scheduled Task** → **User-defined script**
3. Task name: `BEC CRM Daily Backup`
4. Schedule: Daily at 2:00 AM
5. Script:
   ```bash
   cd /volume1/docker/bec-crm
   docker-compose exec -T postgres pg_dump -U crm_user crm_db | gzip > /volume1/docker/bec-crm/backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz

   # Keep only last 30 days of backups
   find /volume1/docker/bec-crm/backups -name "backup_*.sql.gz" -mtime +30 -delete
   ```

### Configure Monitoring

1. Enable **notifications** in DSM for:
   - High CPU usage
   - High memory usage
   - Docker container status changes

2. Set up health check monitoring (optional):
   - Use Synology built-in monitoring
   - Or external tools like Uptime Robot

### Enable HTTPS (Production)

For production deployment with custom domains:

1. **Option A:** Use Synology Let's Encrypt
   - Control Panel → Security → Certificate
   - Add certificate for your domains

2. **Option B:** Use Caddy (included in production compose)
   - Update `Caddyfile` with your domains
   - Deploy with: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

### Configure External Integrations

If using Zapier or ggLeap:

1. Update `.env` with API keys
2. Set `FEATURE_MESSAGING=true` or `FEATURE_GGLEAP_SYNC=true`
3. Restart containers: `docker-compose restart`

---

## Updating the Application

```bash
# SSH into NAS
ssh admin@your-nas-ip

# Navigate to project
cd /volume1/docker/bec-crm

# Pull latest changes (if using Git)
git pull

# Or upload new files via File Station

# Rebuild and restart
docker-compose down
docker-compose pull
docker-compose up -d

# Run any new migrations
docker-compose exec api alembic upgrade head
```

---

## Support Resources

- **Documentation:** See `/docs` folder
- **Troubleshooting:** See `TROUBLESHOOTING.md`
- **Training:** See `ADMIN_TRAINING.md` and `STAFF_TRAINING.md`
- **Backups:** See `BACKUP_AND_MAINTENANCE.md`
- **API Docs:** `http://YOUR_NAS_IP:8000/docs`

---

## Security Best Practices

1. **Change default passwords** immediately
2. **Use strong passwords** for all accounts
3. **Enable HTTPS** for production access
4. **Restrict network access** to local network only (unless remote access needed)
5. **Keep DSM and Docker updated**
6. **Regular backups** (automated daily)
7. **Monitor access logs** periodically
8. **Disable unused features** via feature flags

---

## Quick Reference Commands

```bash
# Start system
docker-compose up -d

# Stop system
docker-compose down

# Restart system
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Backup database
docker-compose exec postgres pg_dump -U crm_user crm_db | gzip > backup.sql.gz

# Restore database
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U crm_user crm_db

# Access API shell
docker-compose exec api bash

# Access database shell
docker-compose exec postgres psql -U crm_user crm_db
```

---

**Installation Complete!**

Your BEC CRM system is now running on your Synology NAS.

For training and daily operations, see:
- `ADMIN_TRAINING.md` - Admin user guide
- `STAFF_TRAINING.md` - Staff user guide
- `KIOSK_SETUP.md` - Kiosk configuration guide
