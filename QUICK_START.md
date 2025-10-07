# BEC CRM Quick Start Guide

**5-Minute Quick Reference**

---

## 🚀 Installation (30 Minutes)

### 1. Generate Certificate (5 min)
```bash
cd ~/certs
openssl req -new -x509 -days 3650 -nodes \
  -keyout bec.local.key -out bec.local.crt \
  -subj "/C=US/ST=CA/L=Bakersfield/O=BEC/CN=*.bec.local"
```

### 2. Configure pfSense DNS (5 min)
```
Services → DNS Resolver → Host Overrides

krc.bec.local     → 192.168.1.100
kiosk.bec.local   → 192.168.1.100
```

### 3. Install CRM (10 min)
```bash
cd /opt
git clone <repo> CRM
cd CRM
mkdir -p infra/certs
cp ~/certs/bec.local.* infra/certs/

# Generate secrets
openssl rand -hex 32  # SECRET_KEY
openssl rand -hex 32  # JWT_SECRET_KEY

# Edit .env
nano .env
# Update: APP_ENV, SECRET_KEY, JWT_SECRET_KEY, CORS_ORIGINS

# Start services
docker compose up -d
docker compose exec api alembic upgrade head
```

### 4. Create Admin (5 min)
```bash
docker compose exec api python
```
```python
from apps.api.models import User
from modules.core_auth.utils import hash_password
from core.database import SessionLocal
import uuid

db = SessionLocal()
admin = User(
    id=uuid.uuid4(),
    email="admin@bakersfieldesports.com",
    password_hash=hash_password("YOUR_SECURE_PASSWORD"),
    role="admin",
    is_active=True
)
db.add(admin)
db.commit()
exit()
```

### 5. Install Certificate on Clients (5 min)
**Windows:** Double-click `bec.local.crt` → Install → Trusted Root CA
**Mac:** Double-click → Keychain → Trust → Always Trust
**iOS:** Email cert → Install → Trust in Settings

---

## 🔐 Access URLs

- **Admin:** https://krc.bec.local
- **Kiosk:** https://kiosk.bec.local
- **API Docs:** https://krc.bec.local/api/v1/docs
- **Health:** https://krc.bec.local/api/v1/healthz

---

## 👥 User Roles

### Admin Can:
✅ Create clients
✅ Edit all client fields
✅ Delete clients
✅ Import CSV
✅ Check in clients
✅ Add notes

### Staff Can:
✅ View clients
✅ Check in clients
✅ Edit notes ONLY
❌ Create/delete clients
❌ Edit other fields

---

## 🛠️ Common Commands

```bash
# View services
docker compose ps

# View logs
docker compose logs -f api

# Restart service
docker compose restart api

# Stop all
docker compose down

# Start all
docker compose up -d

# Backup database
docker compose exec postgres pg_dump -U crm_user crm_db > backup.sql

# Access database
docker compose exec postgres psql -U crm_user -d crm_db

# Create user
docker compose exec api python
```

---

## 🔧 Troubleshooting

### Certificate Warning
- Install cert on device
- Restart browser
- Clear cache

### Can't Reach Server
```bash
nslookup krc.bec.local  # Should return 192.168.1.100
ipconfig /flushdns      # Flush DNS cache
```

### Service Not Starting
```bash
docker compose logs caddy
docker compose restart caddy
```

### Permission Issues
- Verify user role in database
- Clear browser cache
- Re-login

---

## 📋 Pre-Production Checklist

- [ ] Strong passwords set
- [ ] .env updated with generated secrets
- [ ] APP_ENV=production
- [ ] CORS_ORIGINS set to https domains only
- [ ] Certificate installed on all devices
- [ ] DNS resolving correctly
- [ ] Admin login works
- [ ] Staff permissions tested (can only edit notes)
- [ ] Kiosk check-in works
- [ ] Backups configured

---

## 📞 Quick Help

**All services healthy?**
```bash
docker compose ps
```

**Check API health:**
```bash
curl https://krc.bec.local/api/v1/healthz -k
```

**View recent errors:**
```bash
docker compose logs --tail=50
```

---

## 📚 Full Documentation

- **INSTALLATION_GUIDE.md** - Complete installation walkthrough
- **PRODUCTION_CHECKLIST.md** - Deployment checklist
- **SECURITY.md** - Security hardening
- **README.md** - System overview

---

**Server IP:** _______________
**Admin Email:** _______________
**Install Date:** _______________
