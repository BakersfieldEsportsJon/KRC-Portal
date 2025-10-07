# BEC CRM Documentation Index

**Complete documentation for Bakersfield eSports Center CRM System**

---

## 📖 Documentation Overview

This system includes comprehensive documentation for installation, deployment, security, and maintenance. Use this index to find what you need quickly.

---

## 🚀 Getting Started

### For New Installations

1. **START HERE:** [QUICK_START.md](QUICK_START.md)
   - 5-minute overview
   - Essential commands
   - Quick troubleshooting

2. **THEN READ:** [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
   - Complete step-by-step installation
   - Certificate generation
   - pfSense DNS configuration
   - Docker deployment
   - User creation
   - Client device setup
   - **Estimated time: 2-3 hours**

### For Production Deployment

1. [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
   - Pre-deployment checklist
   - Environment configuration
   - Security requirements
   - Testing procedures
   - Post-deployment verification

2. [SECURITY.md](SECURITY.md)
   - Security hardening guide
   - Password policies
   - SSL/TLS configuration
   - Access control
   - Audit procedures

3. [PRODUCTION_READY_SUMMARY.md](PRODUCTION_READY_SUMMARY.md)
   - Current system status
   - Completed items
   - Remaining critical tasks
   - Testing matrix

---

## 📚 System Documentation

### Architecture & Features

**[README.md](README.md)**
- System overview
- Architecture diagram
- Features list
- Technology stack
- Development setup
- Available commands
- Testing guide
- Troubleshooting

### Configuration Files

**[.env.example](.env.example)**
- Example environment variables
- Required settings
- Optional features
- Integration configuration

**[config/app.yaml](config/app.yaml)**
- Application settings
- JWT configuration
- Database pool settings
- Messaging configuration
- Scheduled jobs

**[config/modules.yaml](config/modules.yaml)**
- Feature toggles
- Module configuration
- Integration settings

---

## 🔧 Technical Documentation

### Database

**Migrations:**
- Location: `apps/api/alembic/versions/`
- Current version: `002`
- Latest migration: `002_add_notes_and_language_to_clients.py`

**Schema:**
- Core tables: users, clients, memberships, check_ins
- Support tables: tags, contact_methods, consents
- Integration tables: webhooks_out, ggleap_links
- Audit: audit_log

**Commands:**
```bash
# View current version
docker compose exec api alembic current

# Apply migrations
docker compose exec api alembic upgrade head

# View history
docker compose exec api alembic history
```

### API Documentation

**Interactive API Docs:**
- Swagger UI: `https://krc.bec.local/api/v1/docs`
- ReDoc: `https://krc.bec.local/api/v1/redoc`

**Key Endpoints:**
```
POST   /api/v1/clients          [Admin only]
GET    /api/v1/clients          [All staff]
GET    /api/v1/clients/{id}     [All staff]
PATCH  /api/v1/clients/{id}     [Admin: all, Staff: notes only]
DELETE /api/v1/clients/{id}     [Admin only]
POST   /api/v1/auth/login       [Public]
GET    /api/v1/healthz          [Public]
```

### Frontend

**Application:**
- Admin Interface: React SPA at `/`
- Kiosk Interface: React SPA at `/kiosk`
- Built with: React, TypeScript, Tailwind CSS

**Key Components:**
- `ClientsPage.tsx` - Client list with filtering
- `ClientDetailPage.tsx` - Client details and check-in
- `KioskPage.tsx` - Self-service check-in
- `useAuth.tsx` - Authentication hook with role helpers

---

## 🔐 Security Documentation

### Role-Based Access Control

**Roles:**
- `admin` - Full system access
- `staff` - Limited access (view + notes only)

**Frontend Protection:**
- Admin-only buttons hidden for staff
- Edit functionality restricted
- Import/export disabled for staff

**Backend Protection:**
- JWT token authentication
- Role-based endpoint restrictions
- Field-level access control (notes-only for staff)
- 403 Forbidden for unauthorized access

### SSL/TLS Configuration

**Internal HTTPS:**
- Self-signed certificate
- Covers: `*.bec.local`, `krc.bec.local`, `kiosk.bec.local`
- Valid for: 10 years
- Location: `infra/certs/`

**Caddy Configuration:**
- File: `infra/Caddyfile.internal`
- Automatic HTTPS disabled (internal cert used)
- Security headers configured
- Gzip compression enabled

---

## 🛠️ Operational Guides

### Daily Operations

**Start System:**
```bash
cd /opt/CRM
docker compose up -d
```

**Stop System:**
```bash
docker compose down
```

**View Status:**
```bash
docker compose ps
```

**View Logs:**
```bash
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f caddy
```

### Backup & Restore

**Manual Backup:**
```bash
docker compose exec postgres pg_dump -U crm_user crm_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

**Restore:**
```bash
gunzip < backup.sql.gz | docker compose exec -T postgres psql -U crm_user -d crm_db
```

**Automated Backups:**
- Script: `/opt/CRM/backup.sh`
- Schedule: Daily at 2 AM (cron)
- Retention: 30 days

### User Management

**Create User:**
```python
# In Python shell (docker compose exec api python)
from apps.api.models import User
from modules.core_auth.utils import hash_password
from core.database import SessionLocal
import uuid

db = SessionLocal()
user = User(
    id=uuid.uuid4(),
    email="user@example.com",
    password_hash=hash_password("SecurePassword123!"),
    role="staff",  # or "admin"
    is_active=True
)
db.add(user)
db.commit()
```

**List Users:**
```bash
docker compose exec postgres psql -U crm_user -d crm_db -c "SELECT email, role, is_active FROM users;"
```

**Disable User:**
```bash
docker compose exec postgres psql -U crm_user -d crm_db -c "UPDATE users SET is_active=false WHERE email='user@example.com';"
```

---

## 📊 Monitoring & Maintenance

### Health Checks

**Service Health:**
```bash
docker compose ps
# All should show "Up" and "healthy"
```

**API Health:**
```bash
curl https://krc.bec.local/api/v1/healthz -k
# Should return: {"status":"healthy","service":"bec-crm-api"}
```

**Database Connection:**
```bash
docker compose exec postgres psql -U crm_user -d crm_db -c "SELECT 1;"
```

### Log Files

**Docker Logs:**
```bash
# View all logs
docker compose logs

# Specific service
docker compose logs api
docker compose logs postgres
docker compose logs caddy

# Follow logs
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100
```

**Caddy Access Logs:**
```bash
docker compose exec caddy cat /var/log/caddy/krc.log
docker compose exec caddy cat /var/log/caddy/kiosk.log
```

### Performance Monitoring

**Resource Usage:**
```bash
docker stats
```

**Disk Space:**
```bash
df -h /opt/CRM
docker system df
```

**Database Size:**
```bash
docker compose exec postgres psql -U crm_user -d crm_db -c "SELECT pg_size_pretty(pg_database_size('crm_db'));"
```

---

## 🔍 Troubleshooting

### Common Issues

**Issue:** Certificate warning in browser
- **Solution:** See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) Section 9

**Issue:** Cannot reach server
- **Solution:** Check DNS resolution, verify pfSense configuration

**Issue:** Login fails
- **Solution:** Verify credentials, check JWT_SECRET_KEY in .env

**Issue:** Permission denied (403)
- **Solution:** Verify user role, check backend protection is working

**Issue:** Service won't start
- **Solution:** Check logs: `docker compose logs <service>`

### Getting Help

1. **Check logs:**
   ```bash
   docker compose logs --tail=100
   ```

2. **Verify configuration:**
   ```bash
   cat .env
   docker compose config
   ```

3. **Test connectivity:**
   ```bash
   curl https://krc.bec.local/api/v1/healthz -k
   nslookup krc.bec.local
   ```

4. **Review documentation:**
   - Installation: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
   - Production: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
   - Security: [SECURITY.md](SECURITY.md)

---

## 📝 Additional Resources

### Development

**Setup Development Environment:**
```bash
# Use development override
docker compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d
```

**Run Tests:**
```bash
docker compose exec api pytest
```

**Access Python Shell:**
```bash
docker compose exec api python
```

### Feature Flags

Enable/disable features in `config/modules.yaml`:
- Zapier messaging integration
- ggLeap gaming center sync
- Automated notifications

### Integrations

**Zapier Webhooks:**
- Configuration: `.env` ZAPIER_* variables
- Mode: `production` or `dev_log`
- HMAC security enabled

**ggLeap Integration:**
- Configuration: `.env` GGLEAP_* variables
- Group synchronization
- Membership status sync

---

## 📅 Maintenance Schedule

### Daily
- Check service status
- Review error logs

### Weekly
- Review backups
- Check disk space
- Review access logs

### Monthly
- Update Docker images
- Test backup restoration
- Review user accounts
- Security audit

### Quarterly
- Full system backup
- Performance review
- Documentation update
- Security assessment

---

## 📞 Support Information

### Important Files

```
/opt/CRM/
├── QUICK_START.md              ← Start here
├── INSTALLATION_GUIDE.md       ← Full installation
├── PRODUCTION_CHECKLIST.md     ← Deployment checklist
├── SECURITY.md                 ← Security guide
├── PRODUCTION_READY_SUMMARY.md ← System status
├── README.md                   ← System overview
├── .env                        ← Configuration (SECRET!)
├── docker-compose.yml          ← Service definitions
└── infra/
    ├── Caddyfile.internal      ← HTTPS config
    └── certs/                  ← SSL certificates
```

### Key Contacts

**Technical Support:**
- Check documentation first
- Review logs: `docker compose logs`
- Test health: `curl https://krc.bec.local/api/v1/healthz -k`

**Emergency Procedures:**
- Stop services: `docker compose down`
- Restore from backup (see INSTALLATION_GUIDE.md)
- Review PRODUCTION_CHECKLIST.md

---

## ✅ Quick Status Check

Run this to verify system health:

```bash
#!/bin/bash
echo "=== BEC CRM Status Check ==="
echo ""
echo "Services:"
docker compose ps
echo ""
echo "API Health:"
curl -s https://krc.bec.local/api/v1/healthz -k
echo ""
echo "Disk Space:"
df -h / | grep -v tmpfs
echo ""
echo "Latest Logs (API):"
docker compose logs api --tail=10
```

---

**System Version:** 1.0.0
**Documentation Last Updated:** 2025-10-03

For questions about specific topics, refer to the relevant documentation file above.
