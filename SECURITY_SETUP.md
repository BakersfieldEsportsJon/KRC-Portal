# Security Setup Guide

## Important: Secret Rotation Completed

**Date:** 2025-10-15

All secrets have been rotated and are no longer tracked in git. The following secrets have been updated:

- `SECRET_KEY` - Application secret key
- `JWT_SECRET_KEY` - JWT signing key
- `ZAPIER_HMAC_SECRET` - Zapier webhook HMAC secret
- `POSTGRES_PASSWORD` - Database password

## Environment Configuration

### Production Environment (.env.production)

The `.env.production` file contains production secrets and is **NOT tracked in git**. This file must be securely stored and deployed separately.

**Location:** `/path/to/secure/storage/.env.production`

**Deployment:** Copy this file to the production server manually or via secure secrets management system.

### Generating New Secrets

If you need to rotate secrets again, use the following commands:

```bash
# Generate SECRET_KEY (64 hex characters)
docker-compose exec api python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY (64 hex characters)
docker-compose exec api python -c "import secrets; print(secrets.token_hex(32))"

# Generate ZAPIER_HMAC_SECRET (base64 encoded)
docker-compose exec api python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Database Password (32 characters)
docker-compose exec api python -c "import secrets; print(secrets.token_urlsafe(24))"
```

## Secret Rotation Checklist

When rotating secrets:

- [ ] Generate new secrets using commands above
- [ ] Update `.env.production` file
- [ ] Update production deployment environment variables
- [ ] Update database password in PostgreSQL if rotating DB password
- [ ] Update Zapier webhook secret if rotating ZAPIER_HMAC_SECRET
- [ ] Restart all services: `docker-compose restart`
- [ ] Invalidate all existing JWT tokens (users will need to re-login)
- [ ] Test authentication flows after restart

## Database Password Rotation

If rotating the database password:

```bash
# 1. Generate new password
NEW_PASSWORD=$(docker-compose exec -T api python -c "import secrets; print(secrets.token_urlsafe(24))")

# 2. Update PostgreSQL password
docker-compose exec postgres psql -U crm_user -d crm_db -c "ALTER USER crm_user WITH PASSWORD '${NEW_PASSWORD}';"

# 3. Update .env.production
# Update POSTGRES_PASSWORD and DATABASE_URL with new password

# 4. Restart services
docker-compose restart api worker scheduler
```

## Security Best Practices

1. **Never commit `.env.production` or `.env.development` to git**
2. **Use secrets management** (HashiCorp Vault, AWS Secrets Manager, etc.) for production
3. **Rotate secrets regularly** (quarterly recommended)
4. **Monitor for exposed secrets** using tools like GitGuardian or TruffleHog
5. **Use environment-specific secrets** - never reuse dev secrets in production
6. **Backup secrets securely** - store in encrypted password manager or vault
7. **Limit access** - only admins should have access to production secrets
8. **Audit secret access** - log who accesses secrets and when

## Git History Cleanup

**WARNING:** The old secrets were previously tracked in git. To completely remove them from git history:

```bash
# This requires force-pushing and coordinating with all team members
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env.production .env.development' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGEROUS - coordinate with team first)
git push origin --force --all
```

**Note:** After cleaning git history, all team members must re-clone the repository.

## Emergency Response

If secrets are exposed:

1. **Immediately** rotate all exposed secrets
2. Check access logs for unauthorized access
3. Invalidate all JWT tokens
4. Review recent database activity for suspicious queries
5. Notify affected users if data breach occurred
6. Document the incident in security incident log

## Contact

For security concerns or to report vulnerabilities:
- Email: security@bakersfieldesports.com (update with actual contact)
- Create a security issue in GitHub (private security advisories)

---

**Last Updated:** 2025-10-15
**Next Secret Rotation Due:** 2026-01-15 (quarterly)
