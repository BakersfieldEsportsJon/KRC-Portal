# BEC CRM System - Complete Documentation

## Documentation Index

**Version:** 1.0
**Last Updated:** October 2025
**System:** Bakersfield eSports Center CRM

---

## Quick Start

**New to the system?** Start here:

1. **System Administrators:** [Synology Installation Guide](SYNOLOGY_INSTALLATION.md)
2. **Administrators/Managers:** [Admin Training Guide](ADMIN_TRAINING.md)
3. **Front Desk Staff:** [Staff Training Guide](STAFF_TRAINING.md)
4. **Technical Issues:** [Troubleshooting Guide](TROUBLESHOOTING.md)

---

## Complete Documentation Library

### Installation and Setup

#### [Synology Installation Guide](SYNOLOGY_INSTALLATION.md)
**Audience:** System administrators, IT staff

Complete guide for deploying the CRM system on a Synology NAS with Docker.

**Contents:**
- Prerequisites and requirements
- Step-by-step installation
- Network configuration
- Initial setup and user creation
- Port forwarding and reverse proxy
- Post-installation tasks
- Quick reference commands

**Time to complete:** 1-2 hours

---

#### [Kiosk Setup Guide](KIOSK_SETUP.md)
**Audience:** System administrators, facility managers

How to set up a self-service check-in kiosk station.

**Contents:**
- Hardware requirements and recommendations
- Physical setup and mounting
- Software configuration
- Browser kiosk mode setup
- Security and lock-down procedures
- Testing and troubleshooting
- Maintenance procedures

**Time to complete:** 2-3 hours

---

### Training Materials

#### [Admin Training Guide](ADMIN_TRAINING.md)
**Audience:** Administrators, managers, system admins

Comprehensive guide for managing the CRM system.

**Contents:**
- Getting started and first login
- Dashboard overview
- Managing clients and memberships
- User management and permissions
- Check-in management
- Reports and analytics
- System settings
- Best practices
- Common tasks and scenarios

**Training time:** 2-3 hours

---

#### [Staff Training Guide](STAFF_TRAINING.md)
**Audience:** Front desk staff, general users

Simple guide for daily operations and customer service.

**Contents:**
- Basic navigation
- Looking up clients
- Checking in members (manual)
- Managing client information
- Viewing memberships
- Common scenarios (troubleshooting customer issues)
- Best practices

**Training time:** 30-45 minutes

---

### Support and Maintenance

#### [Troubleshooting Guide](TROUBLESHOOTING.md)
**Audience:** All users, especially administrators

Solutions to common problems and issues.

**Contents:**
- System won't start
- Login and authentication issues
- Kiosk problems
- Database issues
- Performance problems
- Network and access issues
- Data issues
- Integration problems
- Getting help

**Reference:** Use as needed when issues arise

---

#### [Backup and Maintenance Guide](BACKUP_AND_MAINTENANCE.md)
**Audience:** System administrators

Critical procedures for data protection and system health.

**Contents:**
- Backup strategy and overview
- Automated backup setup
- Manual backup procedures
- Backup verification
- Database restoration
- Daily/weekly/monthly maintenance tasks
- System updates
- Monitoring and health checks
- Disaster recovery planning

**Reference:** Follow maintenance schedule

---

## Documentation by Role

### For System Administrators / IT Staff

**Getting Started:**
1. [Synology Installation Guide](SYNOLOGY_INSTALLATION.md) - Deploy the system
2. [Kiosk Setup Guide](KIOSK_SETUP.md) - Set up check-in kiosk
3. [Backup and Maintenance Guide](BACKUP_AND_MAINTENANCE.md) - Set up backups

**Day-to-Day:**
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Fix issues
- [Backup and Maintenance Guide](BACKUP_AND_MAINTENANCE.md) - Maintenance tasks

**Training Others:**
- [Admin Training Guide](ADMIN_TRAINING.md) - Train managers
- [Staff Training Guide](STAFF_TRAINING.md) - Train front desk staff

---

### For Administrators / Managers

**Getting Started:**
1. [Admin Training Guide](ADMIN_TRAINING.md) - Learn the system
2. Review relevant sections of [Troubleshooting Guide](TROUBLESHOOTING.md)

**Day-to-Day:**
- [Admin Training Guide](ADMIN_TRAINING.md) - Reference for tasks
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Solve common issues

**Training Staff:**
- [Staff Training Guide](STAFF_TRAINING.md) - Use for staff onboarding

---

### For Front Desk Staff

**Getting Started:**
1. [Staff Training Guide](STAFF_TRAINING.md) - Complete training

**Day-to-Day:**
- [Staff Training Guide](STAFF_TRAINING.md) - Reference for tasks
- Basic sections of [Troubleshooting Guide](TROUBLESHOOTING.md)

---

## Documentation Quick Reference

### Common Tasks

| Task | Document | Section |
|------|----------|---------|
| Install system | [Synology Installation](SYNOLOGY_INSTALLATION.md) | Installation Steps |
| First time login | [Admin Training](ADMIN_TRAINING.md) | Getting Started |
| Add new client | [Admin Training](ADMIN_TRAINING.md) | Managing Clients |
| Add membership | [Admin Training](ADMIN_TRAINING.md) | Managing Memberships |
| Create staff user | [Admin Training](ADMIN_TRAINING.md) | User Management |
| Reset password | [Admin Training](ADMIN_TRAINING.md) | User Management |
| Manual check-in | [Staff Training](STAFF_TRAINING.md) | Checking In Members |
| Look up client | [Staff Training](STAFF_TRAINING.md) | Looking Up Clients |
| Setup kiosk | [Kiosk Setup](KIOSK_SETUP.md) | Complete Guide |
| Create backup | [Backup & Maintenance](BACKUP_AND_MAINTENANCE.md) | Manual Backups |
| Restore backup | [Backup & Maintenance](BACKUP_AND_MAINTENANCE.md) | Restoration Procedures |
| System won't start | [Troubleshooting](TROUBLESHOOTING.md) | System Won't Start |
| Kiosk not working | [Troubleshooting](TROUBLESHOOTING.md) | Kiosk Issues |
| Can't login | [Troubleshooting](TROUBLESHOOTING.md) | Login Issues |

---

## System Information

### Access URLs

**Production:**
- **Admin Interface:** `http://YOUR_NAS_IP:5173`
- **Kiosk Interface:** `http://YOUR_NAS_IP:5173/kiosk`
- **API Documentation:** `http://YOUR_NAS_IP:8000/docs`
- **API Health Check:** `http://YOUR_NAS_IP:8000/api/v1/healthz`

**With Custom Domains:**
- **Admin Interface:** `https://krc.bakersfieldesports.com`
- **Kiosk Interface:** `https://kiosk.bakersfieldesports.com`
- **API:** `https://api.bakersfieldesports.com`

### Default Credentials

**Initial Admin Account:**
- Email: `admin@bakersfieldesports.com`
- Password: `admin123` (must change on first login)

**Initial Staff Account (if seeded):**
- Email: `staff@bakersfieldesports.com`
- Password: `staff123` (must change on first login)

**Database:**
- Username: `crm_user`
- Password: Set in `.env` file
- Database: `crm_db`

---

## System Architecture

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI framework
- PostgreSQL database
- Redis cache
- RQ worker system

**Frontend:**
- React 18+
- TypeScript
- Vite build system
- TailwindCSS

**Infrastructure:**
- Docker containers
- Docker Compose orchestration
- Caddy reverse proxy (production)
- Synology NAS hosting

**Integrations:**
- Zapier webhooks (optional)
- Textla messaging (optional)
- ggLeap gaming center sync (optional)

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Users & Clients                       │
│  (Admins, Staff, Members using Kiosk)                   │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────────┐         ┌──────────┐       ┌──────────┐
   │ Admin  │         │  Kiosk   │       │   API    │
   │   UI   │         │    UI    │       │   Docs   │
   └────────┘         └──────────┘       └──────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                     ┌─────────────┐
                     │  Caddy      │
                     │  (Reverse   │
                     │   Proxy)    │
                     └─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────────┐         ┌──────────┐       ┌──────────┐
   │FastAPI │         │  Redis   │       │   RQ     │
   │  API   │◄───────►│  Cache   │◄─────►│  Worker  │
   └────────┘         └──────────┘       └──────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                     ┌─────────────┐
                     │ PostgreSQL  │
                     │  Database   │
                     └─────────────┘
```

---

## Project Structure

```
CRM/
├── apps/
│   ├── api/              # FastAPI backend
│   ├── web/              # React frontend
│   └── worker/           # Background job processor
│
├── modules/              # Modular features
│   ├── core.auth/        # Authentication
│   ├── core.clients/     # Client management
│   ├── memberships/      # Membership tracking
│   ├── kiosk/           # Check-in system
│   ├── messaging/       # Zapier integration
│   └── ggleap/          # ggLeap sync
│
├── docs/                 # Documentation (you are here!)
│   ├── README.md                      # This file
│   ├── SYNOLOGY_INSTALLATION.md       # Installation guide
│   ├── ADMIN_TRAINING.md              # Admin user guide
│   ├── STAFF_TRAINING.md              # Staff user guide
│   ├── KIOSK_SETUP.md                 # Kiosk configuration
│   ├── TROUBLESHOOTING.md             # Problem solving
│   └── BACKUP_AND_MAINTENANCE.md      # System maintenance
│
├── config/               # Configuration files
│   ├── app.yaml         # Application settings
│   └── modules.yaml     # Feature toggles
│
├── infra/               # Infrastructure
│   ├── docker-compose.yml
│   ├── Caddyfile
│   └── migrations/      # Database migrations
│
├── tests/               # Test suite
├── scripts/             # Utility scripts
├── .env                 # Environment variables (create from .env.example)
└── README.md            # Main project README
```

---

## Getting Help

### Built-In Resources

1. **API Documentation:**
   - Navigate to `http://YOUR_NAS_IP:8000/docs`
   - Interactive API documentation
   - Test endpoints directly

2. **System Health:**
   - Check `http://YOUR_NAS_IP:8000/api/v1/healthz`
   - Returns system status

3. **Application Logs:**
   ```bash
   # View all logs
   docker-compose logs

   # View specific service
   docker-compose logs api
   docker-compose logs postgres
   docker-compose logs worker

   # Follow logs in real-time
   docker-compose logs -f
   ```

### Support Process

1. **Check relevant documentation** for your role
2. **Review [Troubleshooting Guide](TROUBLESHOOTING.md)** for your issue
3. **Collect diagnostic information:**
   - What you were doing
   - What happened
   - What you expected
   - Error messages (exact text)
   - Screenshots (if helpful)
   - System logs
4. **Contact appropriate support:**
   - **Technical issues:** System administrator
   - **Usage questions:** Refer to training guides
   - **Data issues:** Administrator/manager
   - **Emergency:** [Emergency contact]

### Diagnostic Commands

```bash
# Check system status
docker-compose ps

# Check API health
curl http://localhost:8000/api/v1/healthz

# View recent errors
docker-compose logs --tail=100 | grep -i error

# Check disk space
df -h /volume1/docker/bec-crm

# Check database
docker-compose exec postgres psql -U crm_user crm_db -c "SELECT COUNT(*) FROM clients;"
```

---

## Best Practices

### For Administrators

1. **Daily:**
   - Check dashboard for alerts
   - Review backup logs
   - Monitor system health

2. **Weekly:**
   - Review expiring memberships
   - Check system performance
   - Review staff activity (if applicable)

3. **Monthly:**
   - Generate and review reports
   - Test backup restoration
   - Database maintenance
   - Security review

### For Staff

1. **Always:**
   - Log out when leaving desk
   - Keep client information confidential
   - Report issues promptly

2. **Daily:**
   - Greet members warmly
   - Help with kiosk if needed
   - Update client info when changed

### For System Administrators

1. **Critical:**
   - Keep backups running and verified
   - Monitor disk space
   - Apply security updates promptly
   - Document any changes

2. **Regular:**
   - Review logs for issues
   - Test disaster recovery plan
   - Keep documentation updated
   - Monitor system performance

---

## Security Guidelines

### Password Requirements

- **Minimum 12 characters**
- **Uppercase and lowercase letters**
- **At least one number**
- **At least one special character**

### Access Control

- **Admin role:** Full system access
- **Staff role:** Limited to operations
- **No shared passwords**
- **Deactivate users promptly when they leave**

### Data Protection

- **Regular backups** (automated daily)
- **Offsite backup storage**
- **HTTPS for all production access**
- **Firewall rules** to restrict access
- **Regular security updates**

### Privacy

- **Respect client data**
- **Don't share personal information**
- **Secure workstations when away**
- **Follow data protection regulations**

---

## Maintenance Schedule

### Daily (Automated)
- ✓ Database backup at 2:00 AM
- ✓ Log rotation
- ✓ Temporary file cleanup

### Weekly (Manual)
- Review system health
- Check backup success
- Monitor disk space
- Review error logs

### Monthly (Manual)
- Database optimization
- Log archival
- Security updates
- Test backup restoration
- Generate reports

### Quarterly (Manual)
- Full system review
- Disaster recovery test
- User access audit
- Performance review

### Annually (Manual)
- Comprehensive security audit
- Hardware health check
- Backup media replacement
- Documentation review
- Disaster recovery drill

---

## Version History

### Version 1.0 (October 2025)
- Initial documentation release
- Complete installation guide
- Training materials for all roles
- Troubleshooting guide
- Backup and maintenance procedures
- Kiosk setup guide

### System Features
- Client management
- Membership tracking
- Self-service kiosk check-in
- User management with role-based access
- Reports and analytics
- Password management with forced change on first login
- Audit logging

---

## Additional Resources

### Main Project Documentation
- **Project README:** `../README.md` (in project root)
- **API Code:** `../apps/api/`
- **Web Code:** `../apps/web/`

### Configuration Files
- **Environment Variables:** `../.env.example`
- **Application Config:** `../config/app.yaml`
- **Module Config:** `../config/modules.yaml`
- **Docker Compose:** `../docker-compose.yml`

### Scripts
- **Database Seeding:** `../scripts/seed.py`
- **Backup Script:** `../scripts/backup.sh`
- **Migration Scripts:** `../apps/api/alembic/`

---

## Contact Information

### System Details
- **System Name:** BEC CRM System
- **Organization:** Bakersfield eSports Center
- **Installation Location:** [Your facility address]

### Support Contacts
- **System Administrator:** [Name, email, phone]
- **Technical Support:** [Contact information]
- **Emergency Contact:** [Contact information]
- **Manager:** [Name, email, phone]

### Vendor Information
- **Application:** Custom developed
- **Hosting:** Synology NAS
- **Database:** PostgreSQL
- **Support:** [Your support details]

---

## Feedback and Updates

This documentation is maintained to help you use the BEC CRM system effectively.

**Have suggestions?** Contact the system administrator.

**Found an error?** Please report it so we can correct it.

**Need additional documentation?** Let us know what would be helpful.

---

## Document Index

All documentation files in this directory:

1. **[README.md](README.md)** - This file (documentation index)
2. **[SYNOLOGY_INSTALLATION.md](SYNOLOGY_INSTALLATION.md)** - System installation
3. **[ADMIN_TRAINING.md](ADMIN_TRAINING.md)** - Administrator training
4. **[STAFF_TRAINING.md](STAFF_TRAINING.md)** - Staff training
5. **[KIOSK_SETUP.md](KIOSK_SETUP.md)** - Kiosk configuration
6. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solving
7. **[BACKUP_AND_MAINTENANCE.md](BACKUP_AND_MAINTENANCE.md)** - System maintenance

---

**Last Updated:** October 2025
**Documentation Version:** 1.0
**System Version:** 1.0

**Welcome to the BEC CRM System!**

We hope this documentation helps you get the most out of your customer relationship management system. If you have questions or need assistance, please refer to the appropriate guide or contact your system administrator.
