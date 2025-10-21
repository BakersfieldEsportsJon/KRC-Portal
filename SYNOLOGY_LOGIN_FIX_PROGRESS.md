# Synology CRM Login Fix - Progress Report
**Date:** October 20, 2025
**Status:** In Progress - Database Schema Issue Identified

---

## Problem Summary

The CRM application on Synology NAS cannot complete login because the database tables are not being created. The API starts successfully but fails during database initialization with a `DuplicateTableError: relation "ix_users_email" already exists` error.

### Root Cause
SQLAlchemy is attempting to create database indexes that already exist from a previous failed initialization attempt, causing the transaction to rollback. Even though the error is caught, **the tables are never actually created** because the transaction fails.

---

## Changes Pushed to `develop` Branch

### ✅ Completed Changes (Commit: f72c95d)

1. **Fixed Database Initialization** (`apps/api/main.py:72`)
   - Added `checkfirst=True` parameter to `Base.metadata.create_all()`
   - This tells SQLAlchemy to check if tables/indexes exist before creating them
   - Added logging: "Database tables verified/created"

   ```python
   # Create database tables
   async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.create_all, checkfirst=True)
   logger.info("Database tables verified/created")
   ```

2. **Centralized User Model** (`apps/api/models.py`)
   - Moved `User` model from `auth_workaround.py` to `models.py`
   - This ensures all models are defined in one place to avoid ORM conflicts
   - Updated all API files to import User from centralized models:
     - `clients_api.py`
     - `users_api.py`
     - `memberships_api.py`
     - `checkins_api.py`
     - `password_management_api.py`

3. **Added Admin Creation Script** (`create_admin.py`)
   - Simple script to create an admin user
   - Creates user: `admin@bec.com` / `admin123`
   - Note: This file is in the root directory, not in Docker container

---

## Current Status on Synology

### Environment Details
- **Server:** Synology NAS at `10.1.1.5`
- **Installation Path:** `/volume1/docker/KRCCheckin`
- **Database:** PostgreSQL (user: `crm_user`, db: `crm_db`)
- **Ports:** 8080 (HTTP), 8443 (HTTPS)
- **Git Branch:** `develop` (needs to be pulled)

### What's Working
✅ Docker containers are running
✅ API server starts successfully
✅ All API modules register correctly
✅ Health check endpoint works (`http://10.1.1.5:8080/api/v1/healthz`)
✅ Database connection is working

### What's NOT Working
❌ Database tables are not created (empty database)
❌ Cannot create admin user (no `users` table)
❌ Cannot log in (no user data)

### Current Error
```
DuplicateTableError: relation "ix_users_email" already exists
[SQL: CREATE UNIQUE INDEX ix_users_email ON users (email)]
ERROR: Application startup failed. Exiting.
```

---

## What Needs to Happen Next

### Step 1: Pull Latest Changes from Git
The Synology installation is **out of sync** with the latest code. You need to pull the changes:

```bash
cd /volume1/docker/KRCCheckin
git status  # Check current state
git pull origin develop  # Pull latest fixes
```

**Important:** The Synology version is missing:
- The `checkfirst=True` fix in `main.py` ✅ *Actually present but not in Docker container*
- The centralized User model updates ❌ *Missing `username` and `dark_mode` fields*

### Step 2: Rebuild Docker Containers
After pulling, rebuild the API container to use the new code:

```bash
# Stop everything and remove old volumes (fresh start)
sudo docker compose down -v

# Rebuild API container
sudo docker compose build api

# Start all services
sudo docker compose up -d

# Wait for startup
sleep 15
```

### Step 3: Verify Tables Were Created
Check that the database now has tables:

```bash
sudo docker compose exec postgres psql -U crm_user -d crm_db -c "\dt"
```

**Expected output:**
```
                List of relations
 Schema |         Name          | Type  |   Owner
--------+-----------------------+-------+-----------
 public | check_ins             | table | crm_user
 public | client_notes          | table | crm_user
 public | client_tags           | table | crm_user
 public | clients               | table | crm_user
 public | consent               | table | crm_user
 public | contact_methods       | table | crm_user
 public | membership_tiers      | table | crm_user
 public | memberships           | table | crm_user
 public | tags                  | table | crm_user
 public | users                 | table | crm_user
```

If you see "Did not find any relations" - the problem persists.

### Step 4: Create Admin User
Once tables exist, create an admin user:

```bash
sudo docker compose exec api python -m scripts.setup_production_users
```

Choose option `1` to create a new admin account and use:
- **Email:** `jon@bakersfieldesports.com`
- **Password:** Your secure password

### Step 5: Test Login
Open browser: `http://10.1.1.5:8080`
Login with the admin credentials you just created.

---

## Troubleshooting Commands

### Check API Logs
```bash
sudo docker compose logs api | tail -30
```

### Check All Running Containers
```bash
sudo docker compose ps
```

### Restart API Only
```bash
sudo docker compose restart api
```

### Connect to Database Manually
```bash
sudo docker compose exec postgres psql -U crm_user -d crm_db
```

Inside psql:
```sql
\dt              -- List tables
\di              -- List indexes
\d users         -- Describe users table
SELECT * FROM users;  -- View all users
```

### Full Reset (Nuclear Option)
If nothing works, completely reset:
```bash
# Stop and remove everything
sudo docker compose down -v

# Remove any stray volumes
sudo docker volume prune

# Pull latest code
git pull origin develop

# Rebuild everything
sudo docker compose build

# Start fresh
sudo docker compose up -d
```

---

## Key Files Changed

| File | Changes | Purpose |
|------|---------|---------|
| `apps/api/main.py` | Added `checkfirst=True` to database creation | Prevent duplicate index errors |
| `apps/api/models.py` | Added centralized User model | Consolidate model definitions |
| `apps/api/auth_workaround.py` | Removed User model, import from models.py | Use centralized model |
| `apps/api/clients_api.py` | Import User from models.py | Use centralized model |
| `apps/api/users_api.py` | Import User from models.py | Use centralized model |
| `apps/api/memberships_api.py` | Import User from models.py | Use centralized model |
| `apps/api/checkins_api.py` | Import User from models.py | Use centralized model |
| `apps/api/password_management_api.py` | Import User from models.py | Use centralized model |
| `create_admin.py` | New file (root directory) | Simple admin user creation |

---

## Docker Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Caddy (Reverse Proxy)                                  │
│  Port 8080 → Web & API                                  │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴─────────┐
    │                  │
┌───▼─────┐      ┌────▼──────┐
│   Web   │      │    API    │
│ (Vue.js)│      │ (FastAPI) │
└─────────┘      └─────┬─────┘
                       │
              ┌────────┴─────────┐
              │                  │
         ┌────▼─────┐      ┌────▼─────┐
         │ Postgres │      │  Redis   │
         │ Database │      │  Cache   │
         └──────────┘      └──────────┘
              │                  │
         ┌────▼────┐        ┌───▼──────┐
         │ Worker  │        │Scheduler │
         │  (RQ)   │        │   (RQ)   │
         └─────────┘        └──────────┘
```

---

## Environment Configuration

Your `.env` file is configured correctly:
- Database: `crm_db` with user `crm_user`
- CORS Origins: Properly configured for your domains
- Synology IP: `10.1.1.5`

No changes needed to `.env`.

---

## Why This Happened

1. **Initial Problem:** At some point, a previous database initialization failed partway through
2. **Orphaned Indexes:** Some indexes were created but not the tables themselves
3. **Persistent Volumes:** Docker volumes persist data even when containers are stopped
4. **Transaction Rollback:** When SQLAlchemy hit the duplicate index error, it rolled back the entire transaction
5. **Missing checkfirst:** The code didn't tell SQLAlchemy to skip existing objects

The fix (`checkfirst=True`) should resolve this, but you need to:
1. Pull the latest code
2. Rebuild the Docker containers
3. Clear the old volumes (`docker compose down -v`)

---

## Testing Checklist

After completing the steps above, verify:

- [ ] `docker compose ps` shows all containers healthy
- [ ] `\dt` shows 10+ database tables
- [ ] Admin user created successfully
- [ ] Can access `http://10.1.1.5:8080`
- [ ] Can log in with admin credentials
- [ ] Dashboard loads after login
- [ ] No errors in `docker compose logs api`

---

## Next Session Quick Start

When you return to this issue:

1. **Pull latest code:**
   ```bash
   cd /volume1/docker/KRCCheckin
   git pull origin develop
   ```

2. **Fresh rebuild:**
   ```bash
   sudo docker compose down -v
   sudo docker compose build
   sudo docker compose up -d
   ```

3. **Verify tables:**
   ```bash
   sudo docker compose exec postgres psql -U crm_user -d crm_db -c "\dt"
   ```

4. **Create admin:**
   ```bash
   sudo docker compose exec api python -m scripts.setup_production_users
   ```

5. **Test login:**
   Open `http://10.1.1.5:8080`

---

## Support & References

- **Repository:** https://github.com/BakersfieldEsportsJon/KRCCheckin
- **Branch:** `develop`
- **Latest Commit:** f72c95d - "Fix database initialization and centralize User model"

If you encounter issues:
1. Check the logs: `sudo docker compose logs api`
2. Verify file sync: `grep -A 5 "Create database tables" /volume1/docker/KRCCheckin/apps/api/main.py`
3. Check database state: `sudo docker compose exec postgres psql -U crm_user -d crm_db -c "\dt"`

---

**End of Progress Report**
