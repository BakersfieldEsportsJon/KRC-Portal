# Password Management Implementation TODO

**Status:** ⚠️ **NOT IMPLEMENTED** - Requires code changes before production
**Priority:** CRITICAL
**Est. Time:** 4-6 hours

---

## Overview

The current system allows admins to set passwords directly when creating users. This is insecure because:
1. Admins shouldn't know staff passwords
2. Passwords may be shared insecurely (email, text, etc.)
3. No way to ensure users change their initial password

**Required Changes:**
- Implement password setup flow for new users
- Implement admin password reset capability
- Staff CANNOT reset their own passwords (admin-only)

---

## Implementation Requirements

### 1. New User Creation Flow

**Current Behavior (INSECURE):**
```python
# Admin creates user with password
POST /api/v1/users
{
  "email": "staff@example.com",
  "password": "Admin123!",  # ❌ Admin knows the password
  "role": "staff"
}
```

**Required Behavior (SECURE):**
```python
# Admin creates user WITHOUT password
POST /api/v1/users
{
  "email": "staff@example.com",
  "role": "staff"
  # No password field
}

# System generates:
# 1. Random secure token (valid 24 hours)
# 2. Setup link: https://krc.bakersfieldesports.com/setup-password?token=xxx
# 3. Sends email to staff@example.com with setup link
```

### 2. Password Setup Endpoint

Create new endpoint for users to set their initial password:

```python
POST /api/v1/auth/setup-password
{
  "token": "secure-random-token-from-email",
  "password": "NewSecurePassword123!",
  "password_confirm": "NewSecurePassword123!"
}

# Validates:
# - Token is valid and not expired
# - Token hasn't been used
# - Password meets strength requirements
# - Passwords match

# On success:
# - Sets user password
# - Marks token as used
# - Activates user account
# - Returns success message
```

### 3. Admin Password Reset (Staff Cannot Reset Own)

**Admin can reset ANY staff password:**

```python
POST /api/v1/users/{user_id}/reset-password
Authorization: Bearer <admin-token>

# Generates:
# - New secure token (valid 24 hours)
# - Reset link sent to user's email
# - User must use link to set new password

# Response:
{
  "message": "Password reset email sent to user",
  "reset_link_expires": "2025-10-16T14:30:00Z"
}
```

**Staff CANNOT reset their own password:**
- No "Forgot Password" link on login page
- No self-service password reset
- Must contact admin for password reset

---

## Database Changes Required

### Add to `users` table:

```sql
ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(255);
ALTER TABLE users ADD COLUMN password_reset_token_expires TIMESTAMP;
ALTER TABLE users ADD COLUMN password_reset_token_used BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN password_setup_required BOOLEAN DEFAULT TRUE;
```

**OR** create separate table:

```sql
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_by UUID REFERENCES users(id),  -- Admin who initiated reset
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_token (token),
    INDEX idx_user_id (user_id)
);
```

---

## Frontend Changes Required

### 1. Admin User Management Page

**File:** `apps/web/src/pages/AdminPage.tsx`

**Changes:**
- Remove password field from "Create User" form
- Add "Reset Password" button next to each user
- Show toast notification: "Password reset email sent to {user.email}"

### 2. Password Setup Page (NEW)

**File:** `apps/web/src/pages/PasswordSetupPage.tsx` (create new)

**Route:** `/setup-password?token=xxx`

**UI:**
- Read token from URL query parameter
- Show password setup form:
  - New Password field (with strength indicator)
  - Confirm Password field
  - Submit button
- Validate password meets requirements (12+ chars, etc.)
- Show success message and redirect to login

### 3. Remove "Forgot Password" from Login

**File:** `apps/web/src/pages/LoginPage.tsx`

**Changes:**
- Do NOT add "Forgot Password" link
- Add help text: "Contact your administrator to reset your password"

---

## Email Templates Required

### Template 1: New User Welcome + Password Setup

```
Subject: Welcome to KRC Gaming Center - Set Up Your Account

Hi {user_name},

Your administrator has created an account for you at KRC Gaming Center.

To get started, please set up your password by clicking the link below:

{setup_link}

This link will expire in 24 hours.

Password Requirements:
- At least 8 characters long
- Must contain uppercase and lowercase letters
- Must contain at least one number
- Must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

If you did not request this account, please contact your administrator.

Thanks,
KRC Gaming Center Team
```

### Template 2: Password Reset (Admin Initiated)

```
Subject: Password Reset Request for KRC Gaming Center

Hi {user_name},

Your administrator has initiated a password reset for your account.

To reset your password, click the link below:

{reset_link}

This link will expire in 24 hours.

If you did not request this password reset, please contact your administrator immediately.

Thanks,
KRC Gaming Center Team
```

---

## Implementation Steps

### Step 1: Backend (API)
1. Create database migration for token fields
2. Create `PasswordResetToken` model (or add fields to User model)
3. Update `POST /api/v1/users` to NOT accept password
4. Create `POST /api/v1/auth/setup-password` endpoint
5. Create `POST /api/v1/users/{id}/reset-password` endpoint (admin only)
6. Implement token generation (use `secrets.token_urlsafe(32)`)
7. Implement email sending (integrate with existing email service)
8. Add token validation and expiry logic

### Step 2: Frontend
1. Update AdminPage - remove password from create user form
2. Add "Reset Password" button to user list
3. Create PasswordSetupPage component
4. Add route for `/setup-password`
5. Update LoginPage to show admin contact message instead of "Forgot Password"

### Step 3: Testing
1. Test user creation (no password required)
2. Test password setup link generation
3. Test password setup page with valid token
4. Test password setup with expired token
5. Test password setup with used token
6. Test admin password reset flow
7. Test that staff cannot reset their own password

### Step 4: Documentation
1. Update admin guide with password reset procedures
2. Document email template configuration
3. Add troubleshooting guide for common issues

---

## Security Considerations

1. **Token Generation:**
   - Use `secrets.token_urlsafe(32)` for cryptographically secure tokens
   - Tokens should be at least 32 characters long
   - Store hashed version of token in database (optional but recommended)

2. **Token Expiration:**
   - Setup tokens expire after 24 hours
   - Reset tokens expire after 24 hours
   - Check expiration on every use

3. **Token Single Use:**
   - Mark token as used after successful password setup/reset
   - Prevent token reuse attacks

4. **Email Security:**
   - Use HTTPS for all password setup/reset links
   - Include user-specific information in email to prevent phishing
   - Log all password reset attempts for audit trail

5. **Rate Limiting:**
   - Limit password reset requests to 3 per hour per user
   - Prevent abuse of reset functionality

---

## Code Examples

### Generating Secure Token

```python
import secrets
from datetime import datetime, timedelta

def generate_password_reset_token(user_id: UUID) -> dict:
    """Generate a secure password reset token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    return {
        "token": token,
        "expires_at": expires_at,
        "user_id": user_id
    }
```

### Validating Token

```python
def validate_reset_token(token: str, db: Session) -> Optional[User]:
    """Validate password reset token and return user"""
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used_at == None,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

    if not reset_token:
        return None

    return db.query(User).get(reset_token.user_id)
```

### Marking Token as Used

```python
def mark_token_used(token: str, db: Session):
    """Mark token as used to prevent reuse"""
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()

    if reset_token:
        reset_token.used_at = datetime.utcnow()
        db.commit()
```

---

## Alternative: Email-less Setup (If Email Not Available)

If email is not configured yet, use this temporary approach:

1. Admin creates user
2. System generates random secure password
3. Admin sees password ONCE in UI (copy to clipboard)
4. User must change password on first login (force_password_change flag)

**Implementation:**
```python
# When creating user
random_password = secrets.token_urlsafe(16)
user.password_hash = hash_password(random_password)
user.force_password_change = True

# Show in UI (once):
{
  "user": {...},
  "temporary_password": random_password,  # Only returned once
  "message": "Share this password securely with the user. They must change it on first login."
}
```

---

## Testing Checklist

- [ ] Admin can create user without password
- [ ] Setup email sent to new user
- [ ] Setup link works and loads password setup page
- [ ] Password setup page validates password strength
- [ ] Token expires after 24 hours
- [ ] Used tokens cannot be reused
- [ ] Admin can reset any staff password
- [ ] Staff cannot access password reset for themselves
- [ ] Reset email sent with correct link
- [ ] Reset link works and sets new password
- [ ] User can login with new password
- [ ] All password changes are logged

---

## Estimated Effort

- **Backend API Changes:** 2-3 hours
- **Database Migration:** 30 minutes
- **Frontend Changes:** 2-3 hours
- **Email Templates:** 30 minutes
- **Testing:** 1-2 hours
- **Total:** 4-6 hours

---

**Priority:** CRITICAL - Must complete before production deployment
**Assigned To:** (To be assigned)
**Due Date:** Before production launch

---

## Questions?

Contact technical lead or review these resources:
- OWASP Password Reset Best Practices
- Django/FastAPI password reset implementations
- NIST Password Guidelines (SP 800-63B)
