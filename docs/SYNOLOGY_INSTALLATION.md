# Installing KRC CRM on Synology NAS

## Overview

Yes! You can install the KRC CRM system on a Synology NAS. This guide walks you through the complete installation process using Docker on your Synology device.

## Prerequisites

### Hardware Requirements
- Synology NAS with at least 2GB RAM (4GB recommended)
- 10GB free disk space (50GB recommended for logs and backups)
- DSM 7.0 or later (DSM 6.x may work but not tested)

### Software Requirements
- Docker package installed from Package Center
- SSH access enabled (recommended for easier installation)

## Preparation

### Step 1: Install Docker

1. Open **Package Center** on your Synology
2. Search for **Docker** (or **Container Manager** on DSM 7.2+)
3. Click **Install**
4. Wait for installation to complete

### Step 2: Enable SSH Access (Recommended)

1. Go to **Control Panel** ’ **Terminal & SNMP**
2. Check **Enable SSH service**
3. Change port if desired (default is 22)
4. Click **Apply**

### Step 3: Handle Port Conflicts

Synology uses ports 80 and 443 by default for its web interface. You have two options:

#### Option A: Use Alternative Ports (Recommended)

Before installation, you'll modify the release package to use ports 8080 and 8443 instead. This allows both DSM and the CRM to run simultaneously.

#### Option B: Disable Synology Web Services (Not Recommended)

```bash
sudo synoservicectl --stop nginx
sudo synoservicectl --disable nginx
```

**Warning**: This will disable the DSM web interface on ports 80/443. You'll need to access DSM through port 5000 or 5001.

## Installation Process

### Step 1: Transfer Release Package to NAS

Choose one method:

**Method A: Using File Station (GUI)**
1. Open **File Station** in DSM
2. Create a new folder: `/docker/krc-crm/`
3. Upload `krc-crm-v1.0.0.tar.gz` to this folder

**Method B: Using SCP (Command Line from your computer)**
```bash
scp krc-crm-v1.0.0.tar.gz your-username@your-nas-ip:/volume1/docker/
```

### Step 2: SSH into Your NAS

From your computer:
```bash
ssh your-username@your-nas-ip
```

Enter your DSM password when prompted.

### Step 3: Extract the Release Package

```bash
# Navigate to docker directory
cd /volume1/docker/

# Extract the package
tar -xzf krc-crm-v1.0.0.tar.gz

# Enter the directory
cd krc-crm-v1.0.0
```

### Step 4: Configure Ports (If Using Alternative Ports)

Edit the docker-compose.yml file:

```bash
nano docker-compose.yml
```

Find the `caddy` service section and change:
```yaml
services:
  caddy:
    ports:
      - "8080:80"   # Change from "80:80" to "8080:80"
      - "8443:443"  # Change from "443:443" to "8443:443"
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### Step 5: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit with nano
nano .env
```

**Critical settings to change**:

```bash
# Database credentials (use strong passwords!)
POSTGRES_DB=crm_prod
POSTGRES_USER=crm_prod_user
POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD

DATABASE_URL=postgresql://crm_prod_user:CHANGE_THIS_TO_STRONG_PASSWORD@postgres:5432/crm_prod

# JWT Secrets (generate random strings)
JWT_SECRET=CHANGE_THIS_TO_RANDOM_SECRET_KEY_AT_LEAST_32_CHARS
REFRESH_SECRET=CHANGE_THIS_TO_ANOTHER_RANDOM_SECRET_KEY

# Application URLs (adjust port to match your configuration)
# If using port 8080:
VITE_API_URL=http://192.168.1.100:8080/api/v1
CORS_ORIGINS=["http://192.168.1.100:8080"]

# Replace 192.168.1.100 with your NAS IP address
```

**To generate secure random secrets**, you can use:
```bash
openssl rand -hex 32
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Run the Installer

```bash
# Make installer executable
chmod +x install.sh

# Run installer
./install.sh
```

The installer will:
-  Check Docker is installed
-  Check Docker Compose is installed
-  Build all containers (this may take 5-10 minutes)
-  Start all services
-  Display service status

### Step 7: Verify Installation

Check that all containers are running:

```bash
docker-compose ps
```

You should see all services as "Up" and healthy.

View logs to ensure no errors:

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs caddy
```

### Step 8: Create Admin User

```bash
docker-compose exec api python -m scripts.create_admin
```

Follow the prompts to create your first administrator account:
- Enter username
- Enter email
- Enter password (will be hashed securely)

## Accessing Your CRM

### From Local Network

Open a web browser and navigate to:

**If using port 8080 (recommended)**:
```
http://your-nas-ip:8080
```

**If using default port 80**:
```
http://your-nas-ip
```

Replace `your-nas-ip` with your NAS's actual IP address (e.g., `192.168.1.100`)

### From Internet (Optional - Advanced)

To access from outside your network:

1. **Configure Port Forwarding on Your Router**:
   - Forward external port 8443 ’ NAS IP port 8443
   - Forward external port 8080 ’ NAS IP port 8080

2. **Use Synology DDNS or Your Own Domain**:
   - Control Panel ’ External Access ’ DDNS
   - Register a free DDNS name (e.g., `mynas.synology.me`)

3. **Update Environment Variables**:
   ```bash
   cd /volume1/docker/krc-crm-v1.0.0
   nano .env
   ```

   Add your external domain to CORS_ORIGINS:
   ```bash
   CORS_ORIGINS=["http://192.168.1.100:8080","https://mynas.synology.me:8443"]
   VITE_API_URL=https://mynas.synology.me:8443/api/v1
   ```

4. **Restart Containers**:
   ```bash
   docker-compose restart
   ```

5. **Configure Synology Firewall** (see Firewall Configuration section below)

## Managing the CRM on Synology

### Using DSM Docker GUI

1. Open **Docker** (or **Container Manager**)
2. Go to **Container** tab
3. You'll see all KRC CRM containers listed

**To start/stop containers**:
- Select containers
- Click **Action** ’ **Start** or **Stop**

**To view logs**:
- Double-click a container
- Click **Log** tab

### Using Command Line (Recommended)

```bash
# Navigate to CRM directory
cd /volume1/docker/krc-crm-v1.0.0

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Check service status
docker-compose ps
```

### Auto-Start on NAS Reboot

The containers are configured with `restart: unless-stopped`, which means they will automatically start when your NAS boots up. No additional configuration needed!

## Backup Strategy

### Automated Backups with Task Scheduler

Create a scheduled task in DSM to backup the database automatically:

1. **Control Panel** ’ **Task Scheduler**
2. Click **Create** ’ **Scheduled Task** ’ **User-defined script**
3. **General** tab:
   - Task name: `CRM Database Backup`
   - User: `root` (or your admin user)
4. **Schedule** tab:
   - Run on the following days: `Daily`
   - Time: `02:00` (2:00 AM)
5. **Task Settings** tab, enter this script:
   ```bash
   #!/bin/bash
   BACKUP_DIR="/volume1/docker/krc-crm-v1.0.0/backups"
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)

   mkdir -p ${BACKUP_DIR}

   cd /volume1/docker/krc-crm-v1.0.0
   docker-compose exec -T postgres pg_dump -U crm_prod_user crm_prod > ${BACKUP_DIR}/backup_${TIMESTAMP}.sql

   gzip ${BACKUP_DIR}/backup_${TIMESTAMP}.sql

   # Keep only last 30 days of backups
   find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +30 -delete
   ```
6. Click **OK**

### Manual Backup

To backup manually via SSH:

```bash
cd /volume1/docker/krc-crm-v1.0.0

# Create backup directory
mkdir -p backups

# Backup database
docker-compose exec postgres pg_dump -U crm_prod_user crm_prod > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backups/backup_*.sql
```

### Restore from Backup

```bash
cd /volume1/docker/krc-crm-v1.0.0

# Uncompress backup if needed
gunzip backups/backup_20250101_020000.sql.gz

# Restore
docker-compose exec -T postgres psql -U crm_prod_user crm_prod < backups/backup_20250101_020000.sql
```

## Updating to a New Version

### Using the Update Script (Recommended)

```bash
# 1. SSH into your NAS
ssh your-username@your-nas-ip

# 2. Navigate to CRM directory
cd /volume1/docker/krc-crm-v1.0.0

# 3. Stop current version
docker-compose down

# 4. Upload new release to /volume1/docker/

# 5. Extract new version over current directory
cd /volume1/docker
tar -xzf krc-crm-v1.1.0.tar.gz --strip-components=1 -C krc-crm-v1.0.0/

# 6. Run update script (automatically backs up database)
cd krc-crm-v1.0.0
./update.sh
```

### Manual Update Process

```bash
# 1. Backup database first
cd /volume1/docker/krc-crm-v1.0.0
docker-compose exec postgres pg_dump -U crm_prod_user crm_prod > backup_before_update.sql

# 2. Stop services
docker-compose down

# 3. Extract new version
cd /volume1/docker
tar -xzf krc-crm-v1.1.0.tar.gz

# 4. Copy .env file from old version to new
cp krc-crm-v1.0.0/.env krc-crm-v1.1.0/

# 5. Start new version
cd krc-crm-v1.1.0
docker-compose up -d --build

# 6. Verify everything works
docker-compose ps
docker-compose logs -f
```

## Firewall Configuration

### Synology Firewall

To allow access through Synology's firewall:

1. **Control Panel** ’ **Security** ’ **Firewall**
2. If firewall is disabled, you can skip this section
3. If enabled, click **Edit Rules** for your active profile
4. Click **Create**
5. Configure the rule:
   - **Ports**: Select **Custom**
   - Enter ports: `8080` and `8443` (or your chosen ports)
   - **Action**: **Allow**
   - **Source IP**: Leave as `All` or restrict to specific IPs
6. Click **OK**

### Router Port Forwarding (For External Access)

To access from the internet:

1. Log into your router's admin interface
2. Find **Port Forwarding** or **Virtual Server** settings
3. Add forwarding rules:
   - **External Port**: `8080` ’ **Internal IP**: `[Your NAS IP]` ’ **Internal Port**: `8080`
   - **External Port**: `8443` ’ **Internal IP**: `[Your NAS IP]` ’ **Internal Port**: `8443`
4. Save settings

## Troubleshooting

### Port Already in Use Error

If you see "port is already allocated" errors:

**Check what's using the port**:
```bash
sudo netstat -tulpn | grep :80
```

**Solutions**:
- Use alternative ports (8080/8443) as described in Step 4
- Stop conflicting service
- Change to different unused ports

### Permission Denied Errors

If you get permission errors:

```bash
# Fix ownership
sudo chown -R your-username:users /volume1/docker/krc-crm-v1.0.0

# Or run docker commands with sudo
sudo docker-compose up -d --build
```

### Containers Won't Start

**Check container logs**:
```bash
docker-compose logs api
docker-compose logs postgres
```

**Common issues**:
- Database not ready: Wait 30 seconds and check again
- Port conflicts: Change ports in docker-compose.yml
- Out of memory: Close other applications or upgrade NAS RAM

### Can't Access Web Interface

1. **Verify containers are running**:
   ```bash
   docker-compose ps
   ```
   All should show "Up"

2. **Check the correct URL format**:
   - Must include port if not using 80: `http://192.168.1.100:8080`
   - Don't forget `http://` prefix

3. **Check firewall** is allowing the port

4. **Check Caddy logs**:
   ```bash
   docker-compose logs caddy
   ```

### Database Connection Errors

1. **Verify database credentials** in `.env` file match docker-compose.yml
2. **Check PostgreSQL is running**:
   ```bash
   docker-compose ps postgres
   ```
3. **Check database logs**:
   ```bash
   docker-compose logs postgres
   ```
4. **Test database connection**:
   ```bash
   docker-compose exec postgres psql -U crm_prod_user -d crm_prod -c "SELECT 1;"
   ```

### Out of Memory Errors

If your NAS has limited RAM, you can set memory limits:

Edit `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## Resource Monitoring

### In DSM

1. Open **Docker** (or **Container Manager**)
2. Go to **Container** tab
3. View CPU/Memory columns for each container

### Command Line

```bash
# View resource usage for all containers
docker stats

# View specific container
docker stats krc-crm-v100_api_1
```

### Performance Optimization for Low-RAM NAS

If running on a NAS with 2GB RAM or less:

1. **Limit container memory** (see Out of Memory section above)
2. **Close unnecessary DSM packages**
3. **Reduce worker processes** in docker-compose.yml
4. **Monitor resource usage** regularly with `docker stats`

## Security Best Practices

1. **Use Strong Passwords**:
   - Change all default passwords in `.env`
   - Use passwords with 20+ characters
   - Include letters, numbers, and symbols

2. **Keep DSM Updated**:
   - Control Panel ’ Update & Restore
   - Enable auto-update if desired

3. **Enable Firewall**:
   - Control Panel ’ Security ’ Firewall
   - Allow only necessary ports

4. **Use HTTPS for External Access**:
   - Configure SSL certificates
   - Use Let's Encrypt or Synology certificates

5. **Regular Backups**:
   - Set up automated backups (see Backup Strategy)
   - Test restore procedures periodically

6. **Limit SSH Access**:
   - Use key-based authentication
   - Change default SSH port
   - Restrict access by IP if possible

7. **Monitor Logs**:
   - Regularly check `docker-compose logs` for errors
   - Check DSM logs in Control Panel ’ Log Center

## Data Storage Location

All persistent data is stored in Docker volumes on your NAS:

```
/volume1/@docker/volumes/
   crm_postgres_data_prod/     # Database data
   crm_redis_data_prod/        # Cache/session data
   crm_caddy_data/             # Caddy web server data
   crm_caddy_config/           # Caddy configuration
```

**Important**: These volumes persist even if you delete containers (unless you specifically use `docker-compose down -v`).

## Uninstallation

If you need to completely remove the CRM:

```bash
# Stop and remove containers
cd /volume1/docker/krc-crm-v1.0.0
docker-compose down

# Remove application files
cd /volume1/docker
rm -rf krc-crm-v1.0.0
rm krc-crm-v1.0.0.tar.gz

# Remove Docker volumes (WARNING: This deletes ALL data!)
docker volume rm crm_postgres_data_prod
docker volume rm crm_redis_data_prod
docker volume rm crm_caddy_data
docker volume rm crm_caddy_config

# Remove Docker images (optional, saves disk space)
docker image prune -a
```

## Additional Resources

### Documentation Files in Release Package

- `DEPLOYMENT_INSTRUCTIONS.md` - General deployment guide
- `ENVIRONMENT_SETUP.md` - Environment configuration
- `UPDATE_STRATEGY.md` - Safe update procedures
- `QUICK_REFERENCE.md` - Command reference
- `RELEASE_readme.md` - Release-specific information

### Synology Resources

- Synology Community: https://community.synology.com
- Docker on Synology: https://www.synology.com/en-us/dsm/packages/Docker
- Synology Knowledge Base: https://kb.synology.com

### Getting Help

**For CRM application issues**:
- Check logs: `docker-compose logs`
- Review documentation in `docs/` folder
- Check GitHub issues (if repository is available)

**For Synology-specific issues**:
- Synology forums
- Check `/var/log/` on your NAS
- DSM Control Panel ’ Log Center

## Quick Reference Commands

```bash
# Navigate to CRM directory
cd /volume1/docker/krc-crm-v1.0.0

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View status
docker-compose ps

# View logs (follow mode)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Backup database
docker-compose exec postgres pg_dump -U crm_prod_user crm_prod > backup.sql

# Create admin user
docker-compose exec api python -m scripts.create_admin

# Check health
curl http://localhost:8080/api/v1/healthz

# Update containers (rebuild)
docker-compose up -d --build

# View resource usage
docker stats
```

## Summary

Installing the KRC CRM on a Synology NAS is straightforward:

1.  Install Docker from Package Center
2.  Enable SSH
3.  Transfer and extract release package
4.  Configure ports and environment variables
5.  Run installation script
6.  Create admin user
7.  Access via web browser

The main consideration is handling port 80/443 conflicts with DSM by using alternative ports (8080/8443).

Your data is stored safely in Docker volumes and persists across updates and container restarts!
