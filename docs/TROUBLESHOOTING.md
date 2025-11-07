# Troubleshooting Guide

## BEC CRM System - Common Issues and Solutions

**Version:** 1.0
**Last Updated:** October 2025

---

## Table of Contents

1. [System Won't Start](#system-wont-start)
2. [Login and Authentication Issues](#login-and-authentication-issues)
3. [Kiosk Issues](#kiosk-issues)
4. [Database Problems](#database-problems)
5. [Performance Issues](#performance-issues)
6. [Network and Access Issues](#network-and-access-issues)
7. [Data Issues](#data-issues)
8. [Integration Issues](#integration-issues)
9. [Backup and Recovery](#backup-and-recovery)
10. [Getting Help](#getting-help)

---

## System Won't Start

### All Containers Fail to Start

**Symptoms:**
- Docker compose fails
- Containers exit immediately
- Error messages in logs

**Solutions:**

1. **Check Docker is running:**
   ```bash
   docker --version
   docker ps
   ```

2. **Check available resources:**
   - Synology DSM → Resource Monitor
   - Ensure sufficient RAM (4GB+ free)
   - Ensure sufficient disk space (5GB+ free)

3. **Check for port conflicts:**
   ```bash
   # List ports in use
   netstat -tulpn | grep -E '5173|8000|5432|6379'
   ```

   If ports are in use, either:
   - Stop conflicting services
   - Change ports in `docker-compose.yml`

4. **Review compose file syntax:**
   ```bash
   docker-compose config
   ```

5. **Check environment file:**
   ```bash
   # Verify .env exists
   ls -la .env

   # Check for syntax errors
   cat .env | grep -v '^#' | grep -v '^$'
   ```

6. **Reset and restart:**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Specific Container Won't Start

**Check specific container logs:**
```bash
# API container
docker-compose logs api

# Database
docker-compose logs postgres

# Web interface
docker-compose logs web

# Worker
docker-compose logs worker

# Redis
docker-compose logs redis
```

**API Container Issues:**
- Check database connection settings in `.env`
- Verify migrations have run: `docker-compose exec api alembic upgrade head`
- Check for Python errors in logs

**PostgreSQL Container Issues:**
- Check data volume permissions
- Verify `POSTGRES_PASSWORD` is set correctly
- Check disk space for database storage
- Try: `docker-compose exec postgres pg_isready`

**Web Container Issues:**
- Check API is accessible
- Verify environment variables
- Check browser console for errors

**Redis Container Issues:**
- Check redis-data volume permissions
- Verify no other Redis instances running

---

## Login and Authentication Issues

### Cannot Login - "Invalid Credentials"

**Possible Causes:**
- Incorrect email or password
- Account doesn't exist
- Database not seeded

**Solutions:**

1. **Verify account exists:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT email, role FROM users;"
   ```

2. **Reset admin password:**
   ```bash
   docker-compose exec api python scripts/reset_admin_password.py
   ```

3. **Re-seed database if empty:**
   ```bash
   docker-compose exec api python scripts/seed.py
   ```

4. **Check for typos:**
   - Email is case-sensitive
   - Check for extra spaces
   - Ensure caps lock is off

### "Password Must Be Changed" Loop

**Symptoms:**
- Change password, but still prompted
- Can't access system after password change

**Solutions:**

1. **Check browser cookies:**
   - Clear browser cache and cookies
   - Try incognito/private mode
   - Try different browser

2. **Verify password meets requirements:**
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one number
   - At least one special character

3. **Check API logs for errors:**
   ```bash
   docker-compose logs api | grep "password"
   ```

4. **Reset via database:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "UPDATE users SET force_password_change = false WHERE email = 'your@email.com';"
   ```

### Session Expires Too Quickly

**Solutions:**

1. **Increase token expiration in `.env`:**
   ```bash
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60  # Default: 30
   JWT_REFRESH_TOKEN_EXPIRE_DAYS=14    # Default: 7
   ```

2. **Restart API:**
   ```bash
   docker-compose restart api
   ```

### "Unauthorized" or 401 Errors

**Solutions:**

1. **Logout and login again**

2. **Check JWT secret hasn't changed:**
   - Verify `JWT_SECRET_KEY` in `.env`
   - If changed, all users must re-login

3. **Check system time:**
   - Ensure NAS system time is correct
   - JWT tokens are time-sensitive

4. **Clear browser storage:**
   ```javascript
   // In browser console
   localStorage.clear();
   sessionStorage.clear();
   ```

---

## Kiosk Issues

### Kiosk Can't Find Clients by Phone

**Symptoms:**
- Enter phone number, no results found
- Client exists in admin interface

**Solutions:**

1. **Check phone number format:**
   - Must be exactly 10 digits
   - No dashes, spaces, or parentheses
   - No country code (+1)
   - Example: `5551234567` ✓
   - Example: `555-123-4567` ✗
   - Example: `(555) 123-4567` ✗

2. **Verify client has phone number:**
   - Check admin interface
   - Ensure phone is saved in contact methods

3. **Check database directly:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT name, phone FROM clients WHERE phone LIKE '%555%';"
   ```

4. **Check API logs:**
   ```bash
   docker-compose logs api | grep "phone"
   ```

5. **Test API directly:**
   ```bash
   curl "http://localhost:8000/api/v1/clients/lookup/phone/5551234567"
   ```

### Kiosk Check-In Button Doesn't Work

**Solutions:**

1. **Check browser console for errors:**
   - Press F12 → Console tab
   - Look for JavaScript errors

2. **Verify API is accessible:**
   ```bash
   curl http://localhost:8000/api/v1/healthz
   ```

3. **Check network connectivity:**
   - Ensure kiosk device can reach NAS
   - Try: `ping YOUR_NAS_IP`

4. **Check CORS settings:**
   - Verify kiosk URL in `CORS_ORIGINS` in `.env`

5. **Reload kiosk page:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Kiosk Shows Wrong Information

**Solutions:**

1. **Clear browser cache:**
   - Ctrl+Shift+Delete → Clear cache

2. **Force refresh:**
   - Ctrl+Shift+R or Cmd+Shift+R

3. **Check database data:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT * FROM clients WHERE id = 'CLIENT_ID';"
   ```

### Kiosk Exits Fullscreen Mode

**Solutions:**

1. **Use kiosk mode:**
   - Chrome: `chrome --kiosk http://YOUR_NAS_IP:5173/kiosk`
   - Prevents user from exiting

2. **Use browser extensions:**
   - "Kiosk Mode" extensions available for Chrome/Firefox
   - Lock down browser navigation

3. **Disable keyboard shortcuts:**
   - Use group policy (Windows) or similar restrictions
   - Disable F11, Alt+Tab, etc.

---

## Database Problems

### Database Connection Failed

**Symptoms:**
- API can't connect to database
- Error: "connection refused" or "connection timeout"

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   docker-compose ps postgres
   docker-compose exec postgres pg_isready
   ```

2. **Verify connection settings:**
   - Check `DATABASE_URL` in `.env`
   - Ensure password matches `POSTGRES_PASSWORD`

3. **Check database logs:**
   ```bash
   docker-compose logs postgres
   ```

4. **Restart database:**
   ```bash
   docker-compose restart postgres
   ```

5. **Check network between containers:**
   ```bash
   docker-compose exec api ping postgres
   ```

### Database Locked or Slow Queries

**Solutions:**

1. **Check active connections:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT count(*) FROM pg_stat_activity;"
   ```

2. **Check for long-running queries:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT pid, usename, query, state FROM pg_stat_activity WHERE state = 'active';"
   ```

3. **Kill stuck query (if needed):**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT pg_terminate_backend(PID);"
   ```

4. **Check disk space:**
   ```bash
   df -h /volume1/docker/bec-crm/data
   ```

### Migration Errors

**Symptoms:**
- `alembic upgrade head` fails
- Database schema mismatch

**Solutions:**

1. **Check current migration version:**
   ```bash
   docker-compose exec api alembic current
   ```

2. **View migration history:**
   ```bash
   docker-compose exec api alembic history
   ```

3. **Force migration to latest:**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. **If completely broken, restore from backup:**
   ```bash
   # See BACKUP_AND_MAINTENANCE.md
   ```

### Data Corruption

**Solutions:**

1. **Check database integrity:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "REINDEX DATABASE crm_db;"
   ```

2. **Restore from most recent backup:**
   - See `BACKUP_AND_MAINTENANCE.md`

3. **Contact support with error logs**

---

## Performance Issues

### System is Slow

**Diagnose Resource Usage:**

1. **Check Synology resources:**
   - DSM → Resource Monitor
   - CPU, RAM, Network, Disk usage

2. **Check Docker container resources:**
   ```bash
   docker stats
   ```

3. **Check database performance:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT * FROM pg_stat_database WHERE datname = 'crm_db';"
   ```

**Solutions:**

1. **Increase RAM allocation (if available)**

2. **Optimize database:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "VACUUM ANALYZE;"
   ```

3. **Clear old data:**
   - Archive old check-ins
   - Remove expired memberships (if desired)

4. **Check network speed:**
   - Use wired connection for kiosk
   - Check WiFi signal strength

5. **Restart containers:**
   ```bash
   docker-compose restart
   ```

### High CPU Usage

**Solutions:**

1. **Identify problematic container:**
   ```bash
   docker stats --no-stream
   ```

2. **Check for runaway processes:**
   - Review API logs
   - Review worker logs

3. **Check background jobs:**
   ```bash
   docker-compose logs worker
   ```

4. **Reduce job frequency** if needed in worker configuration

### High Memory Usage

**Solutions:**

1. **Check which container is using memory:**
   ```bash
   docker stats --no-stream
   ```

2. **Set memory limits in `docker-compose.yml`:**
   ```yaml
   services:
     api:
       mem_limit: 512m
   ```

3. **Reduce connection pool size** (if applicable)

4. **Restart containers to free memory:**
   ```bash
   docker-compose restart
   ```

---

## Network and Access Issues

### Cannot Access from Another Computer

**Solutions:**

1. **Check firewall:**
   - DSM → Control Panel → Security → Firewall
   - Ensure ports 5173 and 8000 are allowed

2. **Verify NAS IP address:**
   ```bash
   ifconfig | grep "inet "
   ```

3. **Test connectivity:**
   ```bash
   # From another computer
   ping YOUR_NAS_IP
   curl http://YOUR_NAS_IP:8000/api/v1/healthz
   ```

4. **Check CORS settings:**
   - Update `CORS_ORIGINS` in `.env` to include accessing IP
   - Restart: `docker-compose restart api`

5. **Use NAS hostname instead of IP:**
   - More reliable on network
   - Example: `http://bec-nas.local:5173`

### CORS Errors in Browser Console

**Symptoms:**
- "Access-Control-Allow-Origin" errors
- API calls fail from browser

**Solutions:**

1. **Update CORS origins in `.env`:**
   ```bash
   CORS_ORIGINS=http://YOUR_NAS_IP:5173,http://localhost:5173,http://kiosk-computer-ip:5173
   ```

2. **Restart API:**
   ```bash
   docker-compose restart api
   ```

3. **Use same domain for all access**

### SSL/HTTPS Issues

**Solutions:**

1. **Check certificate validity:**
   - DSM → Control Panel → Security → Certificate

2. **Regenerate certificate:**
   - Use Let's Encrypt in DSM

3. **Check reverse proxy configuration:**
   - DSM → Control Panel → Login Portal → Advanced → Reverse Proxy

4. **Clear browser SSL cache:**
   - Chrome: chrome://net-internals/#hsts
   - Delete domain security policies

---

## Data Issues

### Client Data Not Showing

**Solutions:**

1. **Check database:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT COUNT(*) FROM clients;"
   ```

2. **Check API response:**
   ```bash
   curl http://localhost:8000/api/v1/clients
   ```

3. **Check browser console** for JavaScript errors

4. **Clear browser cache** and reload

### Membership Status Wrong

**Symptoms:**
- Active membership shows as expired
- Expired membership shows as active

**Solutions:**

1. **Check dates in database:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT id, start_date, end_date, status FROM memberships;"
   ```

2. **Verify system date/time:**
   - Ensure NAS clock is correct
   - Check timezone in `.env`: `TZ=America/Los_Angeles`

3. **Recalculate membership status:**
   - Status is computed automatically
   - Update dates if incorrect

### Check-Ins Not Recording

**Solutions:**

1. **Check API logs:**
   ```bash
   docker-compose logs api | grep "check_in"
   ```

2. **Verify database is writable:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "INSERT INTO check_ins (client_id, method) VALUES ('test', 'phone');"
   ```

3. **Check disk space:**
   ```bash
   df -h /volume1/docker/bec-crm/data
   ```

4. **Test API endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/check-ins \
     -H "Content-Type: application/json" \
     -d '{"client_id": "CLIENT_ID", "method": "phone"}'
   ```

---

## Integration Issues

### Zapier Webhooks Not Sending

**Solutions:**

1. **Check Zapier mode:**
   ```bash
   # In .env
   ZAPIER_MODE=production  # Must be "production" to send
   ```

2. **Verify webhook URL:**
   - Check `ZAPIER_CATCH_HOOK_URL` in `.env`
   - Test URL manually in Zapier

3. **Check HMAC secret:**
   - Ensure `ZAPIER_HMAC_SECRET` matches Zapier configuration

4. **Check worker logs:**
   ```bash
   docker-compose logs worker | grep "zapier"
   ```

5. **Check webhook queue:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT * FROM webhooks_out ORDER BY created_at DESC LIMIT 10;"
   ```

6. **Manually retry failed webhooks:**
   ```bash
   docker-compose exec worker python scripts/retry_webhooks.py
   ```

### ggLeap Sync Not Working

**Solutions:**

1. **Verify feature is enabled:**
   ```bash
   # In .env
   FEATURE_GGLEAP_SYNC=true
   ```

2. **Check API credentials:**
   - Verify `GGLEAP_API_KEY` in `.env`
   - Test key with ggLeap support

3. **Check sync logs:**
   ```bash
   docker-compose logs worker | grep "ggleap"
   ```

4. **Manual sync:**
   ```bash
   docker-compose exec worker python scripts/sync_ggleap.py
   ```

5. **Check network connectivity:**
   - Ensure NAS can reach ggLeap API
   - Test: `curl https://api.ggleap.com`

---

## Backup and Recovery

### Backup Failed

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h /volume1/docker/bec-crm/backups
   ```

2. **Check permissions:**
   ```bash
   ls -la /volume1/docker/bec-crm/backups
   ```

3. **Manual backup:**
   ```bash
   docker-compose exec postgres pg_dump -U crm_user crm_db | gzip > /volume1/docker/bec-crm/backups/manual_backup_$(date +%Y%m%d).sql.gz
   ```

4. **Check Task Scheduler** in DSM

### Cannot Restore Backup

**Solutions:**

1. **Verify backup file exists and is valid:**
   ```bash
   ls -lh /volume1/docker/bec-crm/backups/
   gunzip -t backup_file.sql.gz
   ```

2. **Stop API before restore:**
   ```bash
   docker-compose stop api worker
   ```

3. **Restore database:**
   ```bash
   gunzip -c backup_file.sql.gz | docker-compose exec -T postgres psql -U crm_user crm_db
   ```

4. **Start services:**
   ```bash
   docker-compose start api worker
   ```

5. **Verify data restored:**
   ```bash
   docker-compose exec postgres psql -U crm_user crm_db -c "SELECT COUNT(*) FROM clients;"
   ```

---

## Getting Help

### Collecting Diagnostic Information

When reporting issues, collect this information:

1. **System information:**
   ```bash
   # Synology model and DSM version
   cat /etc.defaults/VERSION

   # Docker version
   docker --version

   # Compose version
   docker-compose --version
   ```

2. **Container status:**
   ```bash
   docker-compose ps
   docker-compose logs --tail=100
   ```

3. **Resource usage:**
   ```bash
   docker stats --no-stream
   ```

4. **Configuration (sanitized):**
   ```bash
   # Remove sensitive info before sharing
   cat .env | sed 's/PASSWORD=.*/PASSWORD=***REDACTED***/g' | sed 's/SECRET=.*/SECRET=***REDACTED***/g'
   ```

5. **Recent errors:**
   ```bash
   docker-compose logs --tail=50 api
   docker-compose logs --tail=50 postgres
   docker-compose logs --tail=50 worker
   ```

### Support Checklist

Before contacting support:

- [ ] Checked this troubleshooting guide
- [ ] Reviewed all container logs
- [ ] Verified disk space available
- [ ] Checked network connectivity
- [ ] Tried restarting containers
- [ ] Checked for recent system changes
- [ ] Collected diagnostic information above

### Emergency Recovery

If system is completely broken:

1. **Stop everything:**
   ```bash
   docker-compose down
   ```

2. **Restore from backup:**
   ```bash
   # See BACKUP_AND_MAINTENANCE.md
   ```

3. **If no backup, re-initialize:**
   ```bash
   docker-compose down -v  # WARNING: Deletes all data
   docker-compose up -d
   docker-compose exec api alembic upgrade head
   docker-compose exec api python scripts/seed.py
   ```

---

## Quick Reference - Common Commands

```bash
# Restart everything
docker-compose restart

# View real-time logs
docker-compose logs -f

# Check container health
docker-compose ps

# Access API shell
docker-compose exec api bash

# Access database shell
docker-compose exec postgres psql -U crm_user crm_db

# Check API health
curl http://localhost:8000/api/v1/healthz

# Clear and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Emergency reset (DELETES ALL DATA)
docker-compose down -v
docker-compose up -d
```

---

**Still having issues?**

1. Check API documentation: `http://YOUR_NAS_IP:8000/docs`
2. Review installation guide: `SYNOLOGY_INSTALLATION.md`
3. Contact system administrator with diagnostic information above
