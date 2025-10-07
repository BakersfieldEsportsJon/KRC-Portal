# Security Hardening Guide

## 🔐 Critical Security Measures

### 1. Strong Secrets Generation

**Generate cryptographically secure secrets:**
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32

# Generate ZAPIER_HMAC_SECRET
openssl rand -base64 32
```

**⚠️ NEVER:**
- Use default secrets from examples
- Commit secrets to version control
- Share secrets in Slack/email
- Reuse secrets across environments

### 2. Password Security

**Current Implementation:**
- ✅ Argon2ID password hashing (industry best practice)
- ✅ Server-side validation
- ✅ Secure password storage

**Production Requirements:**
- [ ] Remove/disable all demo accounts (`admin@bakersfieldesports.com`, `staff1@bakersfieldesports.com`)
- [ ] Require strong passwords (min 12 chars, mixed case, numbers, symbols)
- [ ] Change default admin password immediately
- [ ] Implement password rotation policy

**Recommended Password Policy:**
```python
# Add to modules/core_auth/utils.py
def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements"""
    if len(password) < 12:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in '!@#$%^&*()' for c in password):
        return False
    return True
```

### 3. Database Security

**Connection Security:**
```bash
# .env - Use SSL for production database
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

**Access Control:**
- [ ] Create dedicated database user for application
- [ ] Grant minimum required permissions
- [ ] Disable public schema access
- [ ] Enable audit logging

**Example:**
```sql
-- Create application user
CREATE USER crm_app WITH PASSWORD 'strong_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE crm_db TO crm_app;
GRANT USAGE ON SCHEMA public TO crm_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO crm_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO crm_app;

-- Revoke dangerous permissions
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

### 4. API Security

**✅ Implemented:**
- JWT token authentication
- Role-based access control (Admin/Staff)
- CORS configuration
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM

**⚠️ Additional Recommended:**

#### Rate Limiting
Add to `apps/api/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes:
@router.post("/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, ...):
    ...
```

#### Request Size Limits
```python
# In main.py
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["krc.bakersfieldesports.com", "kiosk.bakersfieldesports.com"]
)
```

### 5. CORS Configuration

**Production CORS:**
```python
# .env
CORS_ORIGINS=https://krc.bakersfieldesports.com,https://kiosk.bakersfieldesports.com

# ⚠️ NEVER use wildcard (*) in production
# ❌ CORS_ORIGINS=*
```

### 6. HTTPS & TLS

**✅ Caddy Configuration (Already Implemented):**
- Automatic Let's Encrypt SSL certificates
- HTTP to HTTPS redirect
- TLS 1.2+ only
- HSTS headers

**Verify Configuration:**
```bash
# Test SSL grade
curl -I https://krc.bakersfieldesports.com

# Should see:
# - Strict-Transport-Security header
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
```

### 7. Docker Security

**Current Setup:**
```yaml
# docker-compose.yml - Good practices already in place:
restart: unless-stopped  # ✅ Auto-restart
healthcheck: ...         # ✅ Health monitoring
```

**Additional Hardening:**
```yaml
# Add to docker-compose.yml services:
security_opt:
  - no-new-privileges:true
read_only: true  # For stateless containers
tmpfs:
  - /tmp
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # Only if needed
```

### 8. Environment Variables Security

**✅ Current Practice:**
- Secrets in `.env` file (not committed)
- Loaded at runtime

**Production Best Practice:**
- [ ] Use Docker secrets for sensitive values
- [ ] Set restrictive file permissions: `chmod 600 .env`
- [ ] Consider using HashiCorp Vault or AWS Secrets Manager

**Example with Docker Secrets:**
```yaml
# docker-compose.yml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt

services:
  api:
    secrets:
      - db_password
      - jwt_secret
```

---

## 🛡️ Input Validation & Sanitization

### Client Data Validation

**✅ Already Implemented:**
```python
# Phone validation
@validator('phone')
def validate_phone(cls, v):
    cleaned = v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+1', '')
    if not cleaned.isdigit() or len(cleaned) != 10:
        raise ValueError('Phone number must be 10 digits')
    return v
```

**Additional Recommended:**
- Email validation (already using Pydantic's `EmailStr` ✅)
- XSS protection for text fields
- SQL injection protection (ORM handles ✅)
- Command injection prevention

### File Upload Security (if implemented)

```python
# If adding file uploads:
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file(file):
    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file type")

    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Scan for malware (recommended)
    # Use ClamAV or similar
```

---

## 🔍 Logging & Monitoring

### Security Event Logging

**Implement audit logging for:**
- [ ] Failed login attempts
- [ ] Successful logins
- [ ] Permission denied (403) errors
- [ ] Client data modifications (especially by staff)
- [ ] User creation/deletion
- [ ] Password changes

**Example:**
```python
# Add to modules/core_auth/router.py
@router.post("/auth/login")
async def login(...):
    try:
        # ... authentication logic
        logger.info(f"Successful login: {user.email} from {request.client.host}")
    except AuthenticationError:
        logger.warning(f"Failed login attempt: {credentials.email} from {request.client.host}")
        raise
```

### Monitoring Checklist

- [ ] Set up alerts for:
  - Multiple failed login attempts
  - 403 Forbidden errors
  - Database connection failures
  - Disk space < 20%
  - Memory usage > 80%
- [ ] Regular log review (weekly)
- [ ] Implement intrusion detection

---

## 🚨 Incident Response Plan

### If Security Breach Suspected:

1. **Immediate Actions:**
   ```bash
   # Stop services
   docker compose down

   # Block suspected IPs in firewall
   sudo ufw deny from <IP_ADDRESS>

   # Rotate all secrets
   # Generate new SECRET_KEY, JWT_SECRET_KEY
   ```

2. **Investigation:**
   - Review access logs
   - Check database for unauthorized changes
   - Review recent user activity
   - Identify entry point

3. **Remediation:**
   - Patch vulnerability
   - Reset compromised passwords
   - Revoke tokens
   - Restore from clean backup if needed

4. **Prevention:**
   - Update security measures
   - Document incident
   - Implement additional monitoring

---

## 📋 Security Audit Checklist

### Monthly Review:
- [ ] Review user accounts - disable inactive
- [ ] Check for failed login attempts
- [ ] Review database access logs
- [ ] Update dependencies: `docker compose pull`
- [ ] Check for security advisories
- [ ] Verify backups are working
- [ ] Test restore procedure

### Quarterly Review:
- [ ] Penetration testing
- [ ] Security patch review
- [ ] Access control review
- [ ] Password policy audit
- [ ] Third-party integration review (Zapier, ggLeap)

---

## 🔗 Webhook Security

### Zapier Integration

**✅ Already Implemented:**
- HMAC-SHA256 signature validation
- Retry logic with exponential backoff

**Verify Configuration:**
```python
# modules/messaging/ - Ensure HMAC validation is active
def verify_zapier_signature(payload: bytes, signature: str) -> bool:
    """Verify Zapier webhook signature"""
    expected_signature = hmac.new(
        settings.ZAPIER_HMAC_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

**Production Requirements:**
- [ ] Use HTTPS URLs only
- [ ] Validate HMAC signatures
- [ ] Set `ZAPIER_MODE=production`
- [ ] Monitor for failed webhook deliveries

---

## 🌐 Network Security

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Consider using fail2ban for SSH protection
sudo apt install fail2ban
```

### Internal Network Isolation

```yaml
# docker-compose.yml - Create internal network
networks:
  internal:
    internal: true
  external:
    internal: false

services:
  postgres:
    networks:
      - internal  # Not exposed to internet

  api:
    networks:
      - internal
      - external  # Exposed via Caddy
```

---

## 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

---

## ✅ Security Sign-Off

Before going to production, verify:

- [ ] All secrets generated and unique
- [ ] Default passwords changed/removed
- [ ] HTTPS working on all domains
- [ ] Role-based access tested
- [ ] Database access restricted
- [ ] Backups encrypted and tested
- [ ] Monitoring and alerts configured
- [ ] Security audit completed
- [ ] Incident response plan documented

---

**Security Contact:** [Your Contact Information]
**Last Security Review:** 2025-10-03
**Next Review Due:** [Date]
