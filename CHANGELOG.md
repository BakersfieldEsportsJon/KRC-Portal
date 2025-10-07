# Changelog

All notable changes to the BEC CRM project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Automated testing suite (unit, integration, E2E)
- Rate limiting for API endpoints
- Enhanced audit logging
- Performance optimization
- Error tracking integration (Sentry)

---

## [1.0.0] - 2025-10-03

### Added - New Features
- **Client Management**
  - Full CRUD operations for clients
  - Notes field for staff annotations
  - Language preference field
  - UCI Number field (renamed from POS Number)
  - POS/Service coordinator fields
  - POS start/end dates
  - CSV import/export functionality
  - Client search with multiple filters
  - Client list filtering (All, Active, Expiring, Expired, No Membership)

- **Role-Based Access Control**
  - Admin role: Full system access
  - Staff role: Limited access (view clients, check-in, edit notes only)
  - Frontend UI adapts based on user role
  - Backend API enforces role-based permissions
  - 403 Forbidden responses for unauthorized actions

- **Authentication & Authorization**
  - JWT token-based authentication
  - Argon2ID password hashing
  - HTTP Bearer token scheme
  - Access token (30 min) and refresh token (7 days)
  - MFA support (field ready, not yet implemented)
  - Secure login/logout flows

- **Membership Management**
  - Create and track client memberships
  - Membership status calculation (active, expiring, expired)
  - Multiple membership plans support
  - Automatic expiration tracking
  - 30-day expiring soon warning

- **Check-In System**
  - Staff-assisted check-ins
  - Kiosk self-service check-ins (ready)
  - Check-in history tracking
  - Method tracking (kiosk vs staff)
  - Station tracking

- **Database**
  - PostgreSQL 16 with async support
  - Proper migrations with Alembic
  - UUID primary keys
  - Indexed foreign keys
  - Audit timestamps (created_at, updated_at)
  - 13 core tables

- **API Features**
  - FastAPI with async/await
  - Automatic OpenAPI/Swagger documentation
  - Health check endpoint
  - Comprehensive error handling
  - Request/response logging
  - CORS configuration

- **Frontend Features**
  - React 18 with TypeScript
  - React Query for caching
  - Tailwind CSS styling
  - Responsive design
  - Real-time updates
  - Toast notifications
  - Loading states

- **Integrations (Ready)**
  - Zapier webhook support
  - ggLeap gaming center integration
  - Textla messaging service
  - HMAC signature validation

- **Documentation**
  - Comprehensive installation guide
  - Production deployment checklist
  - Security hardening guide
  - Quick start reference
  - Code analysis report
  - API documentation (auto-generated)

### Security
- **Authentication**
  - JWT token authentication with HS256
  - Argon2ID password hashing (industry best practice)
  - Secure token storage
  - Automatic token refresh

- **Authorization**
  - Role-based access control (Admin/Staff)
  - Backend API protection on all endpoints
  - Frontend UI protection
  - 403 Forbidden for unauthorized access

- **Input Validation**
  - Pydantic models for all API inputs
  - Type checking with TypeScript
  - Email validation
  - Phone number validation
  - Date parsing with error handling
  - SQL injection protection (ORM)

- **HTTPS Support**
  - Internal HTTPS configuration
  - Self-signed certificate support
  - Caddy reverse proxy with security headers
  - HSTS, X-Frame-Options, CSP headers

- **Secrets Management**
  - Environment-based configuration
  - .env file (not committed)
  - .env.example template
  - Configurable secret keys

### Database Migrations
- **Migration 001**: Initial schema
  - Users table with authentication
  - Clients table with basic info
  - Memberships table
  - Check-ins table
  - Tags, consents, contact methods
  - Webhooks and integrations

- **Migration 002**: Client enhancements (2025-10-03)
  - Added `notes` field (TEXT) to clients table
  - Added `language` field (VARCHAR 50) to clients table
  - Indexed for performance

### Fixed
- **Critical: Client Update Endpoint** (2025-10-03)
  - Fixed role-based access control for client updates
  - Staff can now edit notes field only
  - Admin can edit all fields
  - Proper 403 error for unauthorized field updates
  - Added notes and language to schemas

- **Migration Cleanup**
  - Removed broken migration (aa15a4a1c755) that had dangerous DROP TABLE commands
  - Verified migration chain integrity

### Changed
- **UI Terminology**
  - Renamed "POS Number" to "UCI Number" throughout UI
  - Updated all labels and form fields

- **Client Filtering**
  - Enhanced filter dropdown with membership status options
  - Added "All Clients", "Active", "Expiring Soon", "Expired", "No Membership"

### Deprecated
- None

### Removed
- Broken migration file (aa15a4a1c755_add_pos_fields_to_clients.py)

### Technical Details
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Reverse Proxy**: Caddy 2
- **Containerization**: Docker, Docker Compose
- **Authentication**: JWT with Argon2ID

### Known Issues
- Auth workaround temporary implementation (will be cleaned up in v1.1.0)
- Scheduler service shows restarting status (non-critical)
- Module import warnings (cosmetic only)

### Breaking Changes
- None (initial release)

---

## Version History

- **v1.0.0** (2025-10-03) - Initial production release
- **v0.1.0** (Development) - Pre-release development version

---

## Versioning Scheme

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR version** (X.0.0): Incompatible API changes
- **MINOR version** (0.X.0): New functionality, backwards-compatible
- **PATCH version** (0.0.X): Bug fixes, backwards-compatible

### Examples:
- `1.0.0` → `1.0.1`: Bug fix (e.g., fix check-in validation)
- `1.0.0` → `1.1.0`: New feature (e.g., add reporting module)
- `1.0.0` → `2.0.0`: Breaking change (e.g., API restructure)

---

## How to Update This Changelog

When making changes:

1. **Add to [Unreleased] section** during development
2. **Move to versioned section** when releasing
3. **Use categories**:
   - `Added` for new features
   - `Changed` for changes in existing functionality
   - `Deprecated` for soon-to-be removed features
   - `Removed` for now removed features
   - `Fixed` for bug fixes
   - `Security` for security improvements

4. **Follow format**:
   ```markdown
   ### Added
   - Brief description of what was added
   - Can include multiple bullet points
   - Reference issue numbers if applicable (#123)
   ```

5. **Update VERSION file** when releasing

---

## Links

- [Source Code Repository](https://github.com/your-org/bec-crm)
- [Issue Tracker](https://github.com/your-org/bec-crm/issues)
- [Documentation](./DOCUMENTATION_INDEX.md)
- [Installation Guide](./INSTALLATION_GUIDE.md)
- [Security Policy](./SECURITY.md)

---

**Maintained by:** Bakersfield eSports Center Development Team
**Contact:** admin@bakersfieldesports.com
