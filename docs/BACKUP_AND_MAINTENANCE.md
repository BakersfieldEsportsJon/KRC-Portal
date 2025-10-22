# Backup and Maintenance Guide

## BEC CRM System - Backup, Recovery, and Maintenance Procedures

**Version:** 1.0
**Last Updated:** October 2025
**Audience:** System administrators

---

## Table of Contents

1. [Backup Overview](#backup-overview)
2. [Automated Backups](#automated-backups)
3. [Manual Backups](#manual-backups)
4. [Backup Verification](#backup-verification)
5. [Restoration Procedures](#restoration-procedures)
6. [Maintenance Tasks](#maintenance-tasks)
7. [System Updates](#system-updates)
8. [Monitoring and Health Checks](#monitoring-and-health-checks)
9. [Disaster Recovery](#disaster-recovery)
10. [Security Maintenance](#security-maintenance)

---

## Backup Overview

### What Gets Backed Up

**Database Backups Include:**
- All client information
- Membership records
- Check-in history
- User accounts
- Contact methods and consents
- Tags and metadata
- Audit logs
- System configuration

**What Is NOT Backed Up:**
- Application code (stored in Git)
- Docker images (can be rebuilt)
- Temporary files
- Session data (Redis)
- Log files (archived separately if needed)

### Backup Strategy

**3-2-1 Backup Rule:**
- **3 copies** of data (original + 2 backups)
- **2 different media types** (NAS + external/cloud)
- **1 offsite copy** (external drive or cloud storage)

**Retention Policy:**
- **Daily backups:** Keep 7 days
- **Weekly backups:** Keep 4 weeks
- **Monthly backups:** Keep 12 months
- **Yearly backups:** Keep indefinitely

---

## Automated Backups

### Setting Up Daily Automated Backups

#### Using Synology Task Scheduler

1. **Open Synology DSM**
2. **Navigate to:** Control Panel → Task Scheduler
3. **Click:** Create → Scheduled Task → User-defined script
4. **Configure Task:**

**General Tab:**
- **Task:** `BEC CRM Daily Backup`
- **User:** `root` (or admin user)
- **Enabled:** ✓

**Schedule Tab:**
- **Run on the following days:** Daily
- **First run time:** 02:00 (2:00 AM)
- **Frequency:** Once a day

**Task Settings Tab:**
- **Send run details by email:** (optional, configure if desired)
- **User-defined script:**

```bash
#!/bin/bash

# Configuration
PROJECT_DIR="/volume1/docker/bec-crm"
BACKUP_DIR="/volume1/docker/bec-crm/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Log start
echo "[$(date)] Starting backup..." >> "${LOG_FILE}"

# Create database backup
cd "${PROJECT_DIR}"
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "[$(date)] Backup successful: ${BACKUP_FILE}" >> "${LOG_FILE}"

    # Verify backup file size (should be > 1KB)
    BACKUP_SIZE=$(stat -c%s "${BACKUP_DIR}/${BACKUP_FILE}")
    if [ $BACKUP_SIZE -gt 1024 ]; then
        echo "[$(date)] Backup verification passed (${BACKUP_SIZE} bytes)" >> "${LOG_FILE}"
    else
        echo "[$(date)] WARNING: Backup file is suspiciously small (${BACKUP_SIZE} bytes)" >> "${LOG_FILE}"
    fi
else
    echo "[$(date)] ERROR: Backup failed!" >> "${LOG_FILE}"
    exit 1
fi

# Clean up old daily backups (keep last 7 days)
find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +7 -delete
echo "[$(date)] Cleaned up backups older than 7 days" >> "${LOG_FILE}"

# Create weekly backup (every Sunday)
if [ $(date +%u) -eq 7 ]; then
    WEEKLY_BACKUP="backup_weekly_${TIMESTAMP}.sql.gz"
    cp "${BACKUP_DIR}/${BACKUP_FILE}" "${BACKUP_DIR}/${WEEKLY_BACKUP}"
    echo "[$(date)] Created weekly backup: ${WEEKLY_BACKUP}" >> "${LOG_FILE}"

    # Clean up old weekly backups (keep last 4 weeks)
    find "${BACKUP_DIR}" -name "backup_weekly_*.sql.gz" -type f -mtime +28 -delete
fi

# Create monthly backup (first day of month)
if [ $(date +%d) -eq 01 ]; then
    MONTHLY_BACKUP="backup_monthly_${TIMESTAMP}.sql.gz"
    cp "${BACKUP_DIR}/${BACKUP_FILE}" "${BACKUP_DIR}/${MONTHLY_BACKUP}"
    echo "[$(date)] Created monthly backup: ${MONTHLY_BACKUP}" >> "${LOG_FILE}"

    # Clean up old monthly backups (keep last 12 months)
    find "${BACKUP_DIR}" -name "backup_monthly_*.sql.gz" -type f -mtime +365 -delete
fi

echo "[$(date)] Backup process completed" >> "${LOG_FILE}"
```

5. **Click OK** to save

### Verifying Automated Backups

**Check Task Scheduler:**
1. Control Panel → Task Scheduler
2. Find "BEC CRM Daily Backup"
3. View "Last Result" and "Last Run Time"
4. Click task → Action → Run to test

**Check Backup Files:**
```bash
# SSH into Synology
ssh admin@your-nas-ip

# List recent backups
ls -lh /volume1/docker/bec-crm/backups/

# Check backup log
tail -n 50 /volume1/docker/bec-crm/backups/backup.log
```

**Expected Output:**
```
backup_20251016_020001.sql.gz    15M    Oct 16 02:00
backup_20251015_020001.sql.gz    15M    Oct 15 02:00
backup_weekly_20251014_020001.sql.gz    15M    Oct 14 02:00
...
```

---

## Manual Backups

### Creating a Manual Backup

**When to create manual backup:**
- Before system updates
- Before major changes
- Before data imports
- When prompted by troubleshooting guide
- For disaster recovery planning

#### Method 1: Using Docker Command (Recommended)

```bash
# SSH into Synology
ssh admin@your-nas-ip

# Navigate to project directory
cd /volume1/docker/bec-crm

# Create backup with timestamp
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Verify backup was created
ls -lh backups/manual_backup_*.sql.gz
```

#### Method 2: Named Backup for Important Events

```bash
# Create backup with descriptive name
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > backups/backup_before_update_$(date +%Y%m%d).sql.gz

# Or with custom name
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > backups/backup_before_major_import.sql.gz
```

#### Method 3: Full System Backup (Files + Database)

```bash
# Create full backup directory
mkdir -p /volume1/docker/bec-crm/backups/full_backup_$(date +%Y%m%d)

# Backup database
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > /volume1/docker/bec-crm/backups/full_backup_$(date +%Y%m%d)/database.sql.gz

# Backup configuration files
cp .env /volume1/docker/bec-crm/backups/full_backup_$(date +%Y%m%d)/
cp docker-compose.yml /volume1/docker/bec-crm/backups/full_backup_$(date +%Y%m%d)/
cp -r config /volume1/docker/bec-crm/backups/full_backup_$(date +%Y%m%d)/

# Create archive
cd /volume1/docker/bec-crm/backups
tar -czf full_backup_$(date +%Y%m%d).tar.gz full_backup_$(date +%Y%m%d)/
```

### Quick Backup Commands

```bash
# Quick daily backup
make backup

# Named backup
make backup-name NAME="before-update"

# List all backups
ls -lh /volume1/docker/bec-crm/backups/

# List backups by date
ls -lt /volume1/docker/bec-crm/backups/ | head -n 10
```

---

## Backup Verification

### Testing Backup Integrity

**Test 1: File Size Check**
```bash
# Backups should be > 1MB typically
ls -lh /volume1/docker/bec-crm/backups/backup_*.sql.gz

# If backup is < 1KB, something is wrong
```

**Test 2: Gunzip Test**
```bash
# Test if file is valid gzip
gunzip -t /volume1/docker/bec-crm/backups/backup_20251016_020001.sql.gz

# No output = success
# Error output = corrupted backup
```

**Test 3: Content Preview**
```bash
# View first 50 lines of backup
gunzip -c /volume1/docker/bec-crm/backups/backup_20251016_020001.sql.gz | head -n 50

# Should see SQL commands and table definitions
```

**Test 4: Full Restore Test (Recommended Monthly)**

See [Restoration Procedures](#restoration-procedures) for detailed steps.

**Create a test restore to verify:**
```bash
# 1. Create test database
docker-compose exec postgres psql -U crm_user -c "CREATE DATABASE test_restore;"

# 2. Restore backup to test database
gunzip -c backups/backup_20251016_020001.sql.gz | docker-compose exec -T postgres pg_restore -U crm_user -d test_restore

# 3. Verify data exists
docker-compose exec postgres psql -U crm_user test_restore -c "SELECT COUNT(*) FROM clients;"

# 4. Clean up test database
docker-compose exec postgres psql -U crm_user -c "DROP DATABASE test_restore;"
```

### Backup Health Checklist

Run monthly:

- [ ] Automated backup task is enabled
- [ ] Recent backups exist (last 7 days)
- [ ] Backup files are appropriate size (> 1MB)
- [ ] Backup log shows no errors
- [ ] Test restore completed successfully
- [ ] Offsite backup is current (if applicable)
- [ ] Backup storage has sufficient space

---

## Restoration Procedures

### When to Restore

- Data corruption detected
- Accidental data deletion
- System failure or crash
- Ransomware or security incident
- Hardware failure
- Migration to new system

### Pre-Restoration Checklist

**BEFORE restoring:**

- [ ] Identify which backup to restore (timestamp/name)
- [ ] Verify backup file integrity
- [ ] Create backup of current state (even if corrupted)
- [ ] Stop all services accessing database
- [ ] Notify staff of downtime
- [ ] Document reason for restoration

### Full Database Restoration

#### Step 1: Stop Services

```bash
# SSH into Synology
ssh admin@your-nas-ip

# Navigate to project
cd /volume1/docker/bec-crm

# Stop API and worker (but keep database running)
docker-compose stop api worker web
```

#### Step 2: Create Safety Backup

```bash
# Backup current state before restore
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > backups/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Step 3: Drop and Recreate Database

```bash
# Drop existing database
docker-compose exec postgres psql -U crm_user postgres -c "DROP DATABASE crm_db;"

# Recreate database
docker-compose exec postgres psql -U crm_user postgres -c "CREATE DATABASE crm_db;"
```

#### Step 4: Restore from Backup

```bash
# Restore database (replace with your backup filename)
gunzip -c backups/backup_20251016_020001.sql.gz | docker-compose exec -T postgres pg_restore -U crm_user -d crm_db

# Or if backup is not gzipped
docker-compose exec -T postgres pg_restore -U crm_user -d crm_db < backups/backup.sql
```

#### Step 5: Verify Restoration

```bash
# Check if tables exist
docker-compose exec postgres psql -U crm_user crm_db -c "\dt"

# Count records in key tables
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT COUNT(*) FROM clients;"
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT COUNT(*) FROM memberships;"
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT COUNT(*) FROM check_ins;"

# Check most recent data
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT * FROM check_ins ORDER BY created_at DESC LIMIT 5;"
```

#### Step 6: Restart Services

```bash
# Start all services
docker-compose start api worker web

# Verify all services are healthy
docker-compose ps

# Check API health
curl http://localhost:8000/api/v1/healthz
```

#### Step 7: Test System

1. **Login to admin interface**
2. **Verify data:**
   - Check client list
   - Verify membership status
   - Check recent check-ins
3. **Test functionality:**
   - Search for clients
   - View check-in history
   - Test kiosk (if applicable)

### Partial Data Restoration

**Restore specific table(s) only:**

```bash
# Export specific table from backup
gunzip -c backups/backup_20251016_020001.sql.gz | docker-compose exec -T postgres pg_restore -U crm_user -d crm_db -t clients

# Or restore specific data using SQL
docker-compose exec postgres psql -U crm_user crm_db < specific_data.sql
```

### Point-in-Time Recovery

**If you need data from specific time:**

1. **Identify backup closest to desired time**
2. **Restore that backup**
3. **Manually add/update data from that point forward**

**Note:** This system doesn't have continuous point-in-time recovery. Recovery is limited to backup timestamps.

---

## Maintenance Tasks

### Daily Maintenance

**Automated (no action needed):**
- Database backup
- Log rotation
- Temporary file cleanup

**Manual Checks:**
- [ ] Review backup log for errors
- [ ] Monitor disk space usage
- [ ] Check system health dashboard

### Weekly Maintenance

```bash
# SSH into Synology
ssh admin@your-nas-ip
cd /volume1/docker/bec-crm

# Check container status
docker-compose ps

# View recent logs for errors
docker-compose logs --tail=100 | grep -i error

# Check disk usage
df -h /volume1/docker/bec-crm

# Database health check
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT pg_database_size('crm_db');"

# Check connection count
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT count(*) FROM pg_stat_activity;"
```

**Checklist:**
- [ ] All containers running and healthy
- [ ] No critical errors in logs
- [ ] Disk space > 20% free
- [ ] Database size is reasonable
- [ ] Recent backups successful
- [ ] System performance acceptable

### Monthly Maintenance

#### Database Optimization

```bash
# Connect to database
docker-compose exec postgres psql -U crm_user crm_db

# Run vacuum and analyze
VACUUM ANALYZE;

# Check for bloat
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

# Exit
\q
```

#### Log Cleanup

```bash
# Archive old Docker logs
docker-compose logs --since 30d > /volume1/docker/bec-crm/backups/logs_archive_$(date +%Y%m).log

# Restart containers to reset log files
docker-compose restart
```

#### Security Updates

```bash
# Update Docker images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

**Checklist:**
- [ ] Database optimized (VACUUM ANALYZE)
- [ ] Old logs archived
- [ ] Docker images updated
- [ ] Test backup restoration
- [ ] Review user accounts (remove inactive)
- [ ] Check storage capacity trends
- [ ] Review audit logs for anomalies
- [ ] Update documentation if needed

### Quarterly Maintenance

- [ ] Review and test disaster recovery plan
- [ ] Audit user access and permissions
- [ ] Review backup retention policy
- [ ] Check for application updates
- [ ] Security audit
- [ ] Performance review
- [ ] Update training materials if needed

### Annual Maintenance

- [ ] Full system review
- [ ] Disaster recovery drill
- [ ] Security penetration test
- [ ] Hardware health check
- [ ] Backup media replacement (external drives)
- [ ] Review and update all documentation
- [ ] Capacity planning for next year

---

## System Updates

### Updating the Application

**Before updating:**
1. Review release notes
2. Create backup
3. Test update in dev environment (if available)
4. Schedule maintenance window
5. Notify users

**Update procedure:**

```bash
# 1. Create backup
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > backups/backup_before_update_$(date +%Y%m%d).sql.gz

# 2. Stop services
docker-compose down

# 3. Pull latest code (if using Git)
git pull origin master

# Or upload new files via File Station

# 4. Pull new Docker images
docker-compose pull

# 5. Start services
docker-compose up -d

# 6. Run database migrations
docker-compose exec api alembic upgrade head

# 7. Verify everything works
docker-compose ps
curl http://localhost:8000/api/v1/healthz

# 8. Test in browser
# Check admin interface
# Check kiosk interface
# Test key functionality
```

### Rolling Back an Update

If update causes problems:

```bash
# 1. Stop services
docker-compose down

# 2. Revert code to previous version
git checkout <previous-commit-hash>

# Or restore previous files

# 3. Restore database if needed
# See "Full Database Restoration" section

# 4. Start services
docker-compose up -d
```

### Updating Synology DSM

1. **Before DSM update:**
   - Create backup of CRM system
   - Note Docker package version
   - Document current configuration

2. **After DSM update:**
   - Verify Docker is still installed
   - Check containers are running
   - Test CRM system access
   - Verify backups still working

---

## Monitoring and Health Checks

### System Health Dashboard

**Check in DSM:**
- Resource Monitor (CPU, RAM, Network, Disk)
- Storage Manager (Disk health)
- Log Center (System events)

### Application Health

**API Health Endpoint:**
```bash
curl http://localhost:8000/api/v1/healthz
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### Container Health

```bash
# Check all containers
docker-compose ps

# Expected: all containers "Up" and "healthy"

# Check specific container logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs worker
```

### Database Health

```bash
# Database size
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT pg_database_size('crm_db');"

# Active connections
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT count(*) FROM pg_stat_activity;"

# Long-running queries
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT pid, usename, query, state FROM pg_stat_activity WHERE state = 'active';"

# Table sizes
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::text)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(tablename::text) DESC;"
```

### Disk Space Monitoring

```bash
# Check overall disk usage
df -h /volume1

# Check project directory usage
du -sh /volume1/docker/bec-crm/*

# Check backup directory size
du -sh /volume1/docker/bec-crm/backups/
```

**Alert thresholds:**
- Warning: < 20% free space
- Critical: < 10% free space

### Setting Up Monitoring Alerts

**Synology DSM Notifications:**

1. **Control Panel** → **Notification**
2. **Enable notifications for:**
   - System overheated
   - Storage space low
   - System crashed
   - Docker container stopped
3. **Configure email or SMS alerts**

**External Monitoring (Optional):**
- Uptime Robot (free tier available)
- Pingdom
- Custom monitoring scripts

---

## Disaster Recovery

### Disaster Scenarios

1. **Hardware Failure:** NAS dies completely
2. **Ransomware:** Files encrypted by malware
3. **Data Corruption:** Database becomes corrupted
4. **Accidental Deletion:** Major data accidentally deleted
5. **Natural Disaster:** Fire, flood, etc. destroys facility

### Disaster Recovery Plan

#### Preparation (Do Now)

1. **Maintain offsite backups:**
   - External USB drive (take home weekly)
   - Cloud storage (Synology C2, Google Drive, etc.)
   - Another location (second facility, owner's home)

2. **Document everything:**
   - System configuration
   - Installation procedures
   - Access credentials (stored securely)
   - Network configuration
   - Integration settings

3. **Test recovery regularly:**
   - Quarterly restore test
   - Annual full disaster recovery drill

#### Recovery Procedure

**Step 1: Assess Situation**
- What failed?
- What data is affected?
- What is the most recent backup?
- What is acceptable data loss?

**Step 2: Acquire Hardware**
- New Synology NAS (same or better specs)
- Or temporary cloud server
- Or spare NAS (if available)

**Step 3: Install Fresh System**
1. Set up new NAS or server
2. Install Docker
3. Create project directories
4. Follow SYNOLOGY_INSTALLATION.md

**Step 4: Restore Configuration**
1. Restore `.env` file
2. Restore `docker-compose.yml`
3. Restore `config/` directory

**Step 5: Restore Database**
1. Start database container only
2. Restore from most recent backup
3. Verify data integrity

**Step 6: Start All Services**
1. Start all containers
2. Run health checks
3. Test all functionality

**Step 7: Verify and Resume**
1. Test with staff
2. Verify recent data
3. Inform users system is restored
4. Document incident and lessons learned

### Recovery Time Objective (RTO)

**Target:** System restored within 4 hours

**Breakdown:**
- Hardware acquisition: 0-2 hours (if spare available)
- System installation: 30 minutes
- Configuration: 30 minutes
- Database restoration: 15 minutes
- Testing and verification: 30 minutes
- Documentation: 30 minutes

### Recovery Point Objective (RPO)

**Target:** Data loss < 24 hours

With daily backups at 2 AM, worst case is losing one day of data.

**To improve RPO:**
- Increase backup frequency (every 6 hours)
- Implement continuous replication
- Use database transaction logs

---

## Security Maintenance

### Security Checklist

**Monthly:**
- [ ] Review user accounts (remove inactive)
- [ ] Check for failed login attempts
- [ ] Review audit logs for suspicious activity
- [ ] Verify backups are encrypted
- [ ] Check for security updates

**Quarterly:**
- [ ] Change admin passwords
- [ ] Review user permissions
- [ ] Test backup encryption
- [ ] Review firewall rules
- [ ] Check SSL certificate validity

**Annually:**
- [ ] Full security audit
- [ ] Penetration testing
- [ ] Update security policies
- [ ] Staff security training

### Security Best Practices

1. **Strong passwords:**
   - Minimum 12 characters
   - Password manager for storage
   - Regular rotation

2. **Access control:**
   - Principle of least privilege
   - Remove access promptly when staff leaves
   - Monitor user activity

3. **Encryption:**
   - HTTPS for all web traffic
   - Encrypted backups
   - Secure credential storage

4. **Updates:**
   - Keep DSM updated
   - Keep Docker updated
   - Keep application updated

5. **Monitoring:**
   - Review logs regularly
   - Alert on suspicious activity
   - Track all administrative actions

---

## Maintenance Calendar Template

### Daily
- 2:00 AM: Automated backup runs
- Morning: Check backup log

### Weekly (Monday)
- Review system health
- Check disk space
- Review error logs

### Monthly (1st Monday)
- Database optimization
- Log cleanup
- Test backup restoration
- Security review

### Quarterly (1st Monday of Jan/Apr/Jul/Oct)
- Full system review
- Disaster recovery test
- User audit
- Performance review

### Annually (January)
- Full security audit
- Disaster recovery drill
- Hardware health check
- Documentation review

---

## Quick Reference Commands

### Backup
```bash
# Manual backup
docker-compose exec -T postgres pg_dump -U crm_user -Fc crm_db | gzip > backups/backup_$(date +%Y%m%d).sql.gz

# List backups
ls -lh backups/

# Test backup integrity
gunzip -t backups/backup_20251016.sql.gz
```

### Restore
```bash
# Stop services
docker-compose stop api worker web

# Restore database
gunzip -c backups/backup_20251016.sql.gz | docker-compose exec -T postgres pg_restore -U crm_user -d crm_db

# Start services
docker-compose start api worker web
```

### Health Checks
```bash
# Container status
docker-compose ps

# API health
curl http://localhost:8000/api/v1/healthz

# Database size
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT pg_database_size('crm_db');"

# Disk space
df -h /volume1/docker/bec-crm
```

### Maintenance
```bash
# Database optimization
docker-compose exec postgres psql -U crm_user crm_db -c "VACUUM ANALYZE;"

# Update application
git pull && docker-compose up -d --build

# View logs
docker-compose logs --tail=100
```

---

## Contacts and Resources

- **System Administrator:** [Your contact]
- **Technical Support:** [Support contact]
- **Emergency Contact:** [Emergency contact]
- **Documentation:** `/volume1/docker/bec-crm/docs/`
- **Backup Location:** `/volume1/docker/bec-crm/backups/`

---

**Remember:** Regular backups and maintenance are your insurance policy. Don't skip them!
