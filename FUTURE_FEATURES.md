# Future Features to Add Later

## Zapier/Textla Messaging Integration
**Status:** Deferred for later implementation
**Priority:** Medium
**Module:** `messaging`

### Features to Add:
- Automated SMS/email campaigns via Zapier webhooks
- Textla SMS integration for member notifications
- Membership expiration reminders
- Check-in reminders for inactive members
- KRC meetup announcements
- Welcome messages for new members

### Configuration Required:
- `ZAPIER_CATCH_HOOK_URL` - Zapier webhook endpoint
- `ZAPIER_HMAC_SECRET` - HMAC signature for security
- `ZAPIER_MODE` - Set to "production" when ready
- `TEXTLA_SENDER` - Textla phone number

### Module Location:
- `/modules/messaging/` (currently disabled in config)

---

## ggLeap Gaming Center Integration
**Status:** Deferred for later implementation
**Priority:** Low
**Module:** `ggleap`

### Features to Add:
- Automatic group synchronization based on membership status
- User linking between CRM and ggLeap
- Auto-sync when membership status changes
- Group mappings (active members, expired members)

### Configuration Required:
- `GGLEAP_API_KEY` - API key for ggLeap
- `GGLEAP_BASE_URL` - API base URL (default: https://api.ggleap.com)
- `FEATURE_GGLEAP_SYNC` - Enable/disable sync

### Module Location:
- `/modules/ggleap/` (currently disabled in config)

---

## Current Module Status

### Enabled (Core System):
- ✅ `core.auth` - Authentication and authorization
- ✅ `core.clients` - Client management
- ✅ `memberships` - Membership tracking with expiration dates
- ✅ `kiosk` - Self-service check-in system

### Disabled (Future):
- ⏸️ `messaging` - Zapier/Textla integration
- ⏸️ `ggleap` - Gaming center integration
- ⏸️ `imports` - Data import tools
- ⏸️ `reports` - Advanced analytics

---

## Notes

When ready to enable these features:

1. **Enable in config/modules.yaml:**
   ```yaml
   messaging:
     enabled: true

   ggleap:
     enabled: true
   ```

2. **Set environment variables** in `.env`

3. **Test thoroughly** before enabling in production

4. **Update worker scheduled jobs** for automated tasks
