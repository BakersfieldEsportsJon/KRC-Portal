# BEC CRM Installation Guide

**Complete Installation Guide for Bakersfield eSports Center CRM System**

**Version:** 1.0.0
**Last Updated:** 2025-10-03
**Estimated Time:** 2-3 hours

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [SSL Certificate Generation](#ssl-certificate-generation)
4. [pfSense DNS Configuration](#pfsense-dns-configuration)
5. [CRM Installation](#crm-installation)
6. [Database Setup](#database-setup)
7. [Create Admin Users](#create-admin-users)
8. [Client Device Configuration](#client-device-configuration)
9. [Verification & Testing](#verification--testing)
10. [Troubleshooting](#troubleshooting)
11. [Post-Installation](#post-installation)

---

## Prerequisites

### Hardware Requirements

**Minimum Server Specs:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 50GB SSD
- Network: 1Gbps Ethernet

**Recommended Server Specs:**
- CPU: 4+ cores
- RAM: 8GB
- Disk: 100GB SSD
- Network: 1Gbps Ethernet

### Software Requirements

- **Operating System:** Ubuntu 22.04 LTS (or Windows Server with Docker Desktop)
- **Docker:** Version 20.10+
- **Docker Compose:** Version 2.0+
- **Git:** Latest version
- **OpenSSL:** For certificate generation

### Network Requirements

- Static IP address for CRM server
- pfSense firewall with DNS Resolver enabled
- Internal network access (192.168.x.x or 10.x.x.x)
- Ports available: 80, 443, 5432, 6379, 8000

---

## 1. Server Setup

### Option A: Ubuntu Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version

# Install Git
sudo apt install git

# Install OpenSSL (usually pre-installed)
openssl version

# Create user for CRM (optional but recommended)
sudo useradd -m -s /bin/bash crm
sudo usermod -aG docker crm
sudo su - crm
```

### Option B: Windows Server

```powershell
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# Install Git
# Download from: https://git-scm.com/download/win

# Install OpenSSL (via Git Bash or download separately)
# Git Bash includes OpenSSL
```

### Set Static IP Address

**Ubuntu:**
```bash
# Edit netplan configuration
sudo nano /etc/netplan/00-installer-config.yaml

# Example configuration:
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses:
          - 192.168.1.1  # pfSense IP

# Apply configuration
sudo netplan apply
```

**Windows:**
- Network Settings → Ethernet → Properties → IPv4
- Set IP: 192.168.1.100
- Subnet: 255.255.255.0
- Gateway: 192.168.1.1 (pfSense IP)
- DNS: 192.168.1.1 (pfSense IP)

---

## 2. SSL Certificate Generation

### Generate Self-Signed Certificate

```bash
# Create certificate directory
mkdir -p ~/certs
cd ~/certs

# Create OpenSSL configuration file
cat > san.cnf << 'EOF'
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=US
ST=California
L=Bakersfield
O=Bakersfield eSports Center
CN=bec.local

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = bec.local
DNS.2 = *.bec.local
DNS.3 = krc.bec.local
DNS.4 = kiosk.bec.local
DNS.5 = localhost
IP.1 = 192.168.1.100
EOF

# Generate certificate (valid for 10 years)
openssl req -new -x509 -days 3650 -nodes \
  -keyout bec.local.key \
  -out bec.local.crt \
  -config san.cnf \
  -extensions v3_req

# Verify certificate
openssl x509 -in bec.local.crt -text -noout | grep -A1 "Subject Alternative Name"

# Expected output should include:
# DNS:bec.local, DNS:*.bec.local, DNS:krc.bec.local, DNS:kiosk.bec.local

# Set proper permissions
chmod 600 bec.local.key
chmod 644 bec.local.crt

echo "✓ Certificate files created:"
ls -lh bec.local.*
```

**Certificate Files Created:**
- `bec.local.crt` - Public certificate (safe to share)
- `bec.local.key` - Private key (keep secure!)

---

## 3. pfSense DNS Configuration

### Configure DNS Resolver (Unbound)

1. **Login to pfSense Web Interface**
   - Navigate to: `https://<pfSense-IP>` (e.g., https://192.168.1.1)
   - Login with admin credentials

2. **Navigate to DNS Resolver**
   - Menu: **Services → DNS Resolver**

3. **Enable DNS Resolver** (if not already enabled)
   - Check "Enable DNS Resolver"
   - Click **Save**

4. **Add Host Overrides**

   Scroll down to **"Host Overrides"** section, click **"Add"**

   **Entry 1 - Admin Interface:**
   ```
   Host: krc
   Domain: bec.local
   IP Address: 192.168.1.100  # Your CRM server IP
   Description: CRM Admin Interface
   ```
   Click **Save**

   **Entry 2 - Kiosk Interface:**
   ```
   Host: kiosk
   Domain: bec.local
   IP Address: 192.168.1.100  # Same server IP
   Description: CRM Kiosk Interface
   ```
   Click **Save**

5. **Apply Changes**
   - Click **"Apply Changes"** button at the top of the page

6. **Verify DNS Configuration**
   ```bash
   # From any client computer (using pfSense as DNS)
   nslookup krc.bec.local
   # Should return: 192.168.1.100

   nslookup kiosk.bec.local
   # Should return: 192.168.1.100
   ```

---

## 4. CRM Installation

### Clone Repository

```bash
# Navigate to installation directory
cd /opt  # Linux
# OR
cd C:\  # Windows

# Clone repository
git clone <repository-url> CRM
cd CRM

# Verify files
ls -la
# Should see: apps/, config/, infra/, docker-compose.yml, etc.
```

### Create Certificate Directory

```bash
# Create directory for SSL certificates
mkdir -p infra/certs

# Copy generated certificates
cp ~/certs/bec.local.crt infra/certs/
cp ~/certs/bec.local.key infra/certs/

# Verify certificates are in place
ls -lh infra/certs/
# Should show: bec.local.crt and bec.local.key
```

### Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Generate secure secrets
echo "Generating secure secrets..."
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
ZAPIER_SECRET=$(openssl rand -base64 32)

echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET"
echo "ZAPIER_HMAC_SECRET=$ZAPIER_SECRET"

# Edit .env file
nano .env  # Linux
# OR
notepad .env  # Windows
```

### Edit `.env` File

Update the following values:

```bash
# Application Environment
APP_ENV=production
SECRET_KEY=<paste-generated-secret-key>
TZ=America/Los_Angeles

# Database (Docker internal connection)
DATABASE_URL=postgresql://crm_user:crm_password@postgres:5432/crm_db

# Redis (Docker internal connection)
REDIS_URL=redis://redis:6379/0

# Authentication
JWT_SECRET_KEY=<paste-generated-jwt-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Internal HTTPS domains
CORS_ORIGINS=https://krc.bec.local,https://kiosk.bec.local

# Hostnames
ADMIN_HOSTNAME=krc.bec.local
KIOSK_HOSTNAME=kiosk.bec.local

# Zapier Integration (update with real values when ready)
ZAPIER_CATCH_HOOK_URL=https://hooks.zapier.com/hooks/catch/your-hook-id/
ZAPIER_HMAC_SECRET=<paste-generated-zapier-secret>
ZAPIER_MODE=production

# Textla Messaging
TEXTLA_SENDER=+18668849961

# ggLeap Integration (optional)
GGLEAP_API_KEY=your-ggleap-api-key-if-using
GGLEAP_BASE_URL=https://api.ggleap.com

# Feature Flags
FEATURE_MESSAGING=true
FEATURE_GGLEAP_SYNC=false  # Set to true if using ggLeap
```

**Save and close the file.**

### Update Docker Compose Configuration

The `docker-compose.yml` file should already be configured for internal HTTPS. Verify these settings:

```yaml
# infra/Caddyfile.internal should be used
caddy:
  volumes:
    - ./infra/Caddyfile.internal:/etc/caddy/Caddyfile:ro
    - ./infra/certs:/etc/caddy/certs:ro
```

This is already configured in your system.

---

## 5. Database Setup

### Start Docker Services

```bash
# Build and start all services
docker compose up -d

# This will start:
# - PostgreSQL database
# - Redis cache
# - API server
# - Web frontend
# - Background worker
# - Scheduler
# - Caddy reverse proxy

# Wait for services to initialize (30-60 seconds)
sleep 60

# Check service status
docker compose ps

# All services should show "Up" and "healthy"
```

**Expected Output:**
```
NAME              STATUS
crm-api-1         Up (healthy)
crm-postgres-1    Up (healthy)
crm-redis-1       Up (healthy)
crm-web-1         Up
crm-worker-1      Up
crm-scheduler-1   Up
crm-caddy-1       Up
```

### Run Database Migrations

```bash
# Apply database schema
docker compose exec api alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, add_notes_and_language_to_clients
```

### Verify Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U crm_user -d crm_db

# Check tables exist
\dt

# Should see tables:
# - users
# - clients
# - memberships
# - check_ins
# - tags
# - etc.

# Exit
\q
```

---

## 6. Create Admin Users

### Create Admin User

```bash
# Access Python shell in API container
docker compose exec api python

# Paste this code:
from apps.api.models import User
from modules.core_auth.utils import hash_password
from core.database import SessionLocal
import uuid

db = SessionLocal()

# Create Admin User
admin = User(
    id=uuid.uuid4(),
    email="admin@bakersfieldesports.com",
    password_hash=hash_password("BEC@Admin2024!Secure"),  # ← CHANGE THIS PASSWORD!
    role="admin",
    is_active=True
)
db.add(admin)
db.commit()
print(f"✓ Created admin user: {admin.email}")

# Create Staff User
staff = User(
    id=uuid.uuid4(),
    email="staff@bakersfieldesports.com",
    password_hash=hash_password("BEC@Staff2024!Secure"),  # ← CHANGE THIS PASSWORD!
    role="staff",
    is_active=True
)
db.add(staff)
db.commit()
print(f"✓ Created staff user: {staff.email}")

# Exit Python
exit()
```

**⚠️ IMPORTANT:** Change the passwords to something secure!

**Password Requirements:**
- Minimum 12 characters
- Mix of uppercase and lowercase
- Include numbers
- Include special characters
- Example: `BEC@2024!SecurePass#Admin`

### Verify Users Created

```bash
# Check users in database
docker compose exec postgres psql -U crm_user -d crm_db -c "SELECT email, role, is_active FROM users;"

# Should show:
#              email              | role  | is_active
# --------------------------------+-------+-----------
#  admin@bakersfieldesports.com   | admin | t
#  staff@bakersfieldesports.com   | staff | t
```

---

## 7. Client Device Configuration

### Install SSL Certificate on Devices

For browsers to trust your self-signed certificate, install it on each device that will access the CRM.

#### Windows Desktop/Laptop

**Method 1: GUI**
1. Copy `bec.local.crt` to the Windows machine
2. Double-click `bec.local.crt`
3. Click **"Install Certificate..."**
4. Select **"Local Machine"**
5. Click **"Next"**
6. Choose **"Place all certificates in the following store"**
7. Click **"Browse"** and select **"Trusted Root Certification Authorities"**
8. Click **"Next"**, then **"Finish"**
9. Click **"Yes"** on the security warning

**Method 2: Command Line (as Administrator)**
```powershell
# Run PowerShell as Administrator
certutil -addstore -f "Root" bec.local.crt
```

#### Mac Desktop/Laptop

1. Copy `bec.local.crt` to the Mac
2. Double-click `bec.local.crt`
3. **Keychain Access** app opens automatically
4. Find the certificate in the list (search for "bec.local")
5. Double-click the certificate
6. Expand the **"Trust"** section
7. Set **"When using this certificate"** to **"Always Trust"**
8. Close window (enter password when prompted)
9. Restart browser

#### Linux Desktop

```bash
# Copy certificate to trusted store
sudo cp bec.local.crt /usr/local/share/ca-certificates/bec.local.crt

# Update certificate store
sudo update-ca-certificates

# Restart browser
```

#### iPad/iOS Tablet (for Kiosk)

1. Email `bec.local.crt` to the iPad or host on internal web server
2. On iPad, download/open the certificate
3. **Settings → Profile Downloaded → Install**
4. Enter passcode
5. Tap **"Install"** (top right)
6. Tap **"Install"** again
7. Tap **"Done"**
8. **Enable Trust:**
   - Go to **Settings → General → About → Certificate Trust Settings**
   - Enable full trust for "bec.local"
9. Restart browser

#### Android Tablet (for Kiosk)

1. Copy `bec.local.crt` to the Android device
2. **Settings → Security → Encryption & Credentials → Install from storage**
3. Browse and select `bec.local.crt`
4. Give it a name (e.g., "BEC CRM")
5. Tap **"OK"**
6. Restart browser

### Configure DNS on Client Devices

**Ensure all client devices use pfSense as their DNS server.**

**Windows:**
1. Network Settings → Ethernet → Properties → IPv4
2. Set DNS Server: `192.168.1.1` (pfSense IP)

**Mac:**
1. System Preferences → Network → Advanced → DNS
2. Add DNS Server: `192.168.1.1` (pfSense IP)

**iOS/Android:**
1. WiFi Settings → Configure Network
2. Set DNS: `192.168.1.1` (pfSense IP)
3. Or configure via DHCP in pfSense to automatically assign

---

## 8. Verification & Testing

### Test DNS Resolution

From any client device:

```bash
# Windows
nslookup krc.bec.local
nslookup kiosk.bec.local

# Mac/Linux
dig krc.bec.local
dig kiosk.bec.local

# Both should return: 192.168.1.100 (your server IP)
```

### Test HTTPS Access

#### Test Admin Interface

1. Open browser on client device
2. Navigate to: `https://krc.bec.local`
3. **Should NOT see certificate warning** (if cert installed correctly)
4. Should see **Login page**

#### Test Kiosk Interface

1. Navigate to: `https://kiosk.bec.local`
2. Should see **Kiosk check-in page**

### Test Admin Login

1. Go to: `https://krc.bec.local`
2. Login with:
   - Email: `admin@bakersfieldesports.com`
   - Password: `<your-admin-password>`
3. Should successfully login and see **Dashboard**

### Test Admin Permissions

As Admin user, verify you can:
- ✓ See **"Add Client"** button
- ✓ See **"Import CSV"** button
- ✓ Click **"Add Client"** and create a test client
- ✓ Edit all client fields
- ✓ Delete the test client
- ✓ Check in a client
- ✓ Add notes to client

### Test Staff Login

1. Logout from admin
2. Login with:
   - Email: `staff@bakersfieldesports.com`
   - Password: `<your-staff-password>`
3. Should successfully login

### Test Staff Permissions

As Staff user, verify:
- ✗ **Cannot** see "Add Client" button
- ✗ **Cannot** see "Import CSV" button
- ✗ **Cannot** see "Edit" button in client list
- ✓ **Can** view client list
- ✓ **Can** view client details
- ✓ **Can** edit client notes (via "Edit Notes" button)
- ✓ **Can** check in clients
- ✗ **Cannot** edit other client fields (should get error)

### Test API Directly

```bash
# Test health endpoint
curl https://krc.bec.local/api/v1/healthz -k

# Expected response:
# {"status":"healthy","service":"bec-crm-api"}

# Test authentication (should fail without token)
curl https://krc.bec.local/api/v1/clients -k

# Expected response:
# {"detail":"Not authenticated"}
```

### Test Kiosk Check-In Flow

1. Create a test client with phone number (as admin)
2. Navigate to: `https://kiosk.bec.local`
3. Enter phone number
4. Click **"Check In"**
5. Should see success message
6. Verify check-in appears in admin interface

---

## 9. Troubleshooting

### Issue: Certificate Warning in Browser

**Symptom:** Browser shows "Not Secure" or certificate warning

**Solutions:**

1. **Verify certificate installed:**
   ```powershell
   # Windows
   certutil -store -user Root | findstr "bec.local"
   ```

2. **Restart browser completely** (close all windows)

3. **Clear browser cache:**
   - Chrome: Settings → Privacy → Clear browsing data
   - Clear cached images and files

4. **Check certificate validity:**
   ```bash
   openssl x509 -in infra/certs/bec.local.crt -text -noout
   ```

5. **Verify Subject Alternative Names:**
   ```bash
   openssl x509 -in infra/certs/bec.local.crt -text -noout | grep -A1 "Subject Alternative Name"
   # Should include: krc.bec.local, kiosk.bec.local
   ```

### Issue: Cannot Reach Server

**Symptom:** Browser shows "Site can't be reached"

**Solutions:**

1. **Check DNS resolution:**
   ```bash
   nslookup krc.bec.local
   # Should return 192.168.1.100
   ```

2. **Verify client using pfSense DNS:**
   ```bash
   ipconfig /all  # Windows
   # DNS Server should be pfSense IP
   ```

3. **Flush DNS cache:**
   ```bash
   ipconfig /flushdns  # Windows
   sudo killall -HUP mDNSResponder  # Mac
   ```

4. **Test direct IP access:**
   ```bash
   # Try accessing via IP
   curl -k https://192.168.1.100
   ```

5. **Check server firewall:**
   ```bash
   # Ubuntu - allow ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

### Issue: Services Not Starting

**Symptom:** `docker compose ps` shows services as "Exited" or "Restarting"

**Solutions:**

1. **Check logs:**
   ```bash
   docker compose logs api
   docker compose logs postgres
   docker compose logs caddy
   ```

2. **Check for port conflicts:**
   ```bash
   # Check if ports are already in use
   sudo netstat -tulpn | grep -E ':(80|443|5432|6379|8000)'
   ```

3. **Restart services:**
   ```bash
   docker compose down
   docker compose up -d
   ```

4. **Check .env file syntax:**
   ```bash
   cat .env
   # Look for syntax errors, missing quotes, etc.
   ```

### Issue: Database Migration Fails

**Symptom:** Error when running `alembic upgrade head`

**Solutions:**

1. **Check database is running:**
   ```bash
   docker compose ps postgres
   # Should show "Up (healthy)"
   ```

2. **Check database connection:**
   ```bash
   docker compose exec postgres psql -U crm_user -d crm_db -c "SELECT 1;"
   ```

3. **View current migration version:**
   ```bash
   docker compose exec api alembic current
   ```

4. **Check migration history:**
   ```bash
   docker compose exec api alembic history
   ```

5. **Force to specific version (if needed):**
   ```bash
   # Stamp database at specific version
   docker compose exec api alembic stamp 001
   docker compose exec api alembic upgrade head
   ```

### Issue: Permission Denied Errors

**Symptom:** Staff can edit fields they shouldn't

**Solutions:**

1. **Check backend is updated:**
   ```bash
   docker compose exec api cat /app/modules/core_clients/router.py | grep require_admin_role
   # Should see require_admin_role in create/delete endpoints
   ```

2. **Restart API:**
   ```bash
   docker compose restart api
   ```

3. **Clear browser cache and re-login**

4. **Verify user role in database:**
   ```bash
   docker compose exec postgres psql -U crm_user -d crm_db -c \
     "SELECT email, role FROM users WHERE email='staff@bakersfieldesports.com';"
   # Should show role = 'staff'
   ```

### Issue: Caddy Won't Start

**Symptom:** Caddy service keeps restarting

**Solutions:**

1. **Check certificate files exist:**
   ```bash
   ls -l infra/certs/
   # Should show bec.local.crt and bec.local.key
   ```

2. **Check certificate permissions:**
   ```bash
   chmod 644 infra/certs/bec.local.crt
   chmod 600 infra/certs/bec.local.key
   ```

3. **Verify Caddyfile syntax:**
   ```bash
   docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile
   ```

4. **Check Caddy logs:**
   ```bash
   docker compose logs caddy --tail=100
   ```

---

## 10. Post-Installation

### Configure Automated Backups

```bash
# Test backup manually
docker compose exec postgres pg_dump -U crm_user crm_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Create backup script
cat > /opt/CRM/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/CRM/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

cd /opt/CRM
docker compose exec -T postgres pg_dump -U crm_user crm_db | gzip > "$BACKUP_DIR/crm_backup_$DATE.sql.gz"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "crm_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: crm_backup_$DATE.sql.gz"
EOF

chmod +x /opt/CRM/backup.sh

# Schedule daily backups via cron
sudo crontab -e

# Add this line (runs at 2 AM daily):
0 2 * * * /opt/CRM/backup.sh >> /var/log/crm_backup.log 2>&1
```

### Configure Log Rotation

```bash
# Create log rotation config
sudo nano /etc/logrotate.d/crm

# Add:
/opt/CRM/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
```

### Set Up Monitoring

```bash
# Create monitoring script
cat > /opt/CRM/monitor.sh << 'EOF'
#!/bin/bash
# Check if services are healthy
docker compose ps | grep -q "unhealthy" && echo "WARNING: Unhealthy services detected!" || echo "All services healthy"

# Check disk space
df -h / | awk 'NR==2 {print "Disk usage: " $5}'

# Check memory
free -h | awk 'NR==2 {print "Memory usage: " $3 "/" $2}'
EOF

chmod +x /opt/CRM/monitor.sh

# Schedule monitoring (every 15 minutes)
sudo crontab -e

# Add:
*/15 * * * * /opt/CRM/monitor.sh >> /var/log/crm_monitor.log 2>&1
```

### Document Credentials

Create a secure document with:
- Server IP address
- Admin username/password
- Staff username/password
- Database credentials
- pfSense admin credentials
- Certificate location

**Store this document securely** (encrypted, password manager, etc.)

### Create Additional Staff Accounts

Follow the same process as admin creation, but with `role="staff"`:

```python
# In Python shell
staff2 = User(
    id=uuid.uuid4(),
    email="another.staff@bakersfieldesports.com",
    password_hash=hash_password("Strong!Password123"),
    role="staff",
    is_active=True
)
db.add(staff2)
db.commit()
```

---

## 11. Quick Reference

### Useful Commands

```bash
# View all services
docker compose ps

# View logs
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f caddy

# Restart a service
docker compose restart api

# Stop all services
docker compose down

# Start all services
docker compose up -d

# Update to latest code
git pull
docker compose down
docker compose up -d --build

# Database backup
docker compose exec postgres pg_dump -U crm_user crm_db > backup.sql

# Database restore
cat backup.sql | docker compose exec -T postgres psql -U crm_user -d crm_db

# Access PostgreSQL
docker compose exec postgres psql -U crm_user -d crm_db

# Access Python shell
docker compose exec api python
```

### Important URLs

- **Admin Interface:** `https://krc.bec.local`
- **Kiosk Interface:** `https://kiosk.bec.local`
- **API Documentation:** `https://krc.bec.local/api/v1/docs`
- **API Health Check:** `https://krc.bec.local/api/v1/healthz`
- **pfSense:** `https://192.168.1.1` (or your pfSense IP)

### Important File Locations

```
/opt/CRM/                           # Main installation directory
├── .env                            # Environment variables
├── docker-compose.yml              # Docker services configuration
├── infra/
│   ├── Caddyfile.internal          # Caddy HTTPS configuration
│   └── certs/
│       ├── bec.local.crt           # SSL certificate
│       └── bec.local.key           # SSL private key
├── apps/
│   ├── api/                        # Backend API
│   ├── web/                        # Frontend application
│   └── worker/                     # Background jobs
└── config/
    ├── app.yaml                    # Application configuration
    └── modules.yaml                # Feature toggles
```

### Default Credentials

**⚠️ CHANGE THESE IMMEDIATELY AFTER INSTALLATION**

- **Admin:** admin@bakersfieldesports.com / [your-secure-password]
- **Staff:** staff@bakersfieldesports.com / [your-secure-password]
- **Database:** crm_user / crm_password (internal only)

---

## Installation Checklist

Use this checklist to track your installation progress:

### Pre-Installation
- [ ] Server meets hardware requirements
- [ ] Static IP assigned to server
- [ ] Docker and Docker Compose installed
- [ ] Git installed
- [ ] OpenSSL available
- [ ] pfSense accessible

### SSL Certificate
- [ ] Certificate generated (`bec.local.crt` and `bec.local.key`)
- [ ] Certificate includes correct domains (SAN)
- [ ] Certificate copied to `infra/certs/`

### pfSense Configuration
- [ ] DNS Resolver enabled
- [ ] Host override for `krc.bec.local` added
- [ ] Host override for `kiosk.bec.local` added
- [ ] DNS changes applied
- [ ] DNS resolution tested

### CRM Installation
- [ ] Repository cloned
- [ ] `.env` file created and configured
- [ ] Secure secrets generated
- [ ] `docker-compose.yml` configured for internal HTTPS
- [ ] Docker services started
- [ ] All services showing "healthy"
- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Staff user created

### Client Configuration
- [ ] Certificate installed on all client devices
- [ ] Client devices using pfSense for DNS
- [ ] DNS resolution tested from clients
- [ ] HTTPS access tested (no warnings)

### Testing
- [ ] Admin login works
- [ ] Admin can create clients
- [ ] Admin can edit all fields
- [ ] Admin can delete clients
- [ ] Staff login works
- [ ] Staff can view clients
- [ ] Staff can edit notes only
- [ ] Staff cannot edit other fields (403 error)
- [ ] Staff cannot create/delete clients (403 error)
- [ ] Kiosk check-in works
- [ ] API health check responds

### Post-Installation
- [ ] Automated backups configured
- [ ] Log rotation configured
- [ ] Monitoring set up
- [ ] Credentials documented securely
- [ ] Additional staff accounts created

---

## Support & Resources

**Documentation:**
- README.md - System overview and features
- PRODUCTION_CHECKLIST.md - Deployment checklist
- SECURITY.md - Security best practices
- PRODUCTION_READY_SUMMARY.md - Status overview

**Logs Location:**
```bash
# Docker logs
docker compose logs -f

# Caddy logs (inside container)
docker compose exec caddy cat /var/log/caddy/krc.log
docker compose exec caddy cat /var/log/caddy/kiosk.log
```

**Getting Help:**
1. Check logs: `docker compose logs`
2. Review troubleshooting section above
3. Check GitHub issues (if available)
4. Verify all checklist items completed

---

## Maintenance Schedule

### Daily
- Check service health: `docker compose ps`
- Review error logs: `docker compose logs --tail=100`

### Weekly
- Review backup logs
- Check disk space: `df -h`
- Review access logs for unusual activity

### Monthly
- Update Docker images: `docker compose pull && docker compose up -d`
- Review and rotate logs
- Test backup restoration
- Review user accounts (disable inactive)
- Security audit (see SECURITY.md)

### Quarterly
- Full system backup
- Performance review
- Security assessment
- Update documentation

---

**Installation Date:** ______________
**Installed By:** ______________
**Server IP:** ______________
**Admin Email:** ______________

---

**End of Installation Guide**

For production deployment checklist, see: `PRODUCTION_CHECKLIST.md`
For security hardening, see: `SECURITY.md`
