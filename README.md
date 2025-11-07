# BEC CRM System

A production-ready Customer Relationship Management and Check-in System built for **Bakersfield eSports Center (BEC)**. This modular monorepo provides comprehensive member management, automated messaging, and seamless kiosk check-in capabilities.

## 🌟 Features

### Core Functionality
- **👥 Client Management**: Complete customer profiles with contact methods, consents, and tagging
- **📅 Membership Tracking**: Automated status updates with expiration notifications
- **🏪 Kiosk Check-in**: Self-service check-in system with phone/code lookup
- **🔐 Role-Based Access**: Secure authentication with admin and staff roles

### Integrations
- **📧 Zapier + Textla Messaging**: Automated SMS/email campaigns with HMAC security
- **🎮 ggLeap Integration**: Automatic group synchronization based on membership status
- **📊 Analytics & Reporting**: Check-in statistics and membership insights

### Technical Features
- **🔧 Modular Architecture**: Feature toggles via configuration
- **🐳 Docker Compose**: Local development and production deployment
- **🔒 Production-Ready Security**: Caddy with Let's Encrypt TLS
- **⚡ Background Jobs**: RQ-based worker system for async tasks
- **🧪 Comprehensive Testing**: Unit, integration, and E2E tests

## 🏗️ Architecture

```
┌─────────────────┬─────────────────┬─────────────────┐
│   Admin UI      │    Kiosk UI     │   API Docs      │
│  (React SPA)    │  (React SPA)    │   (FastAPI)     │
└─────────────────┴─────────────────┴─────────────────┘
                            │
                     ┌─────────────┐
                     │    Caddy    │  ← TLS Termination
                     │  (Reverse   │
                     │   Proxy)    │
                     └─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────────┐        ┌─────────────┐     ┌────────────┐
   │FastAPI │        │   React     │     │ RQ Worker  │
   │  API   │        │    Web      │     │  System    │
   └────────┘        └─────────────┘     └────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
              ┌─────────────────────────────┐
              │     PostgreSQL + Redis      │
              │   (Data + Job Queue)        │
              └─────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Make (optional, for convenience commands)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KRC-Portal
   ```

2. **Quick start (automated)**
   ```bash
   make quick-start
   ```
   This will build images, start services, run migrations, and seed demo data.

3. **Access the applications**
   - **Admin Interface**: http://localhost:5173
   - **Kiosk Interface**: http://localhost:5173/kiosk
   - **API Documentation**: http://localhost:8000/docs

4. **Login credentials**
   - **Admin**: `admin@bakersfieldesports.com` / `admin123`
   - **Staff**: `staff@bakersfieldesports.com` / `staff123`

   **Note**: New users created by admin will be prompted to change their temporary password on first login.

### Manual Setup

1. **Configure environment**
   ```bash
   cp .env.example .env.development
   # Edit .env.development with your settings
   ```

2. **Start development environment**
   ```bash
   make dev
   # or
   docker compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d
   ```

3. **Run database migrations**
   ```bash
   make migrate
   ```

4. **Seed demo data**
   ```bash
   make seed
   ```

## 🛠️ Development

### Available Commands

```bash
# Environment Management
make dev              # Start development environment
make prod             # Start production environment
make down             # Stop all services
make logs             # View all service logs

# Database Operations
make migrate          # Run migrations
make seed            # Seed demo data
make backup          # Create database backup
make restore BACKUP=file.sql.gz  # Restore from backup

# Testing
make test            # Run all tests
make test-unit       # Run unit tests only
make test-e2e        # Run E2E tests only
make test-coverage   # Run with coverage report

# Utilities
make shell-api       # Open API container shell
make shell-db        # Open PostgreSQL shell
make health          # Check service health
make clean           # Clean Docker resources
```

### Project Structure

```
apps/
├── api/             # FastAPI backend application
├── web/             # React frontend application
└── worker/          # RQ background job processor

modules/             # Modular feature system
├── core.auth/       # Authentication & authorization
├── core.clients/    # Client management
├── memberships/     # Membership tracking
├── kiosk/          # Check-in system
├── messaging/      # Zapier/Textla integration
├── ggleap/         # ggLeap gaming center sync
├── imports/        # Data import utilities
└── reports/        # Analytics & reporting

infra/              # Infrastructure configuration
├── docker-compose.yml
├── Caddyfile       # Production reverse proxy
└── migrations/     # Database migration files

config/             # Application configuration
├── app.yaml        # Core application settings
└── modules.yaml    # Feature toggle configuration

tests/              # Comprehensive test suite
scripts/            # Utility scripts
```

### Adding New Features

The system uses a modular architecture where features can be toggled via `config/modules.yaml`:

```yaml
modules:
  new_feature:
    enabled: true
    description: "My new feature"
    features:
      sub_feature: true
```

1. Create module directory in `modules/`
2. Implement `main.py` with `init_module()` function
3. Add database models, API routes, and business logic
4. Enable in `modules.yaml`
5. Restart services to load the new module

## 🌐 Production Deployment

### Prerequisites
- Server with Docker and Docker Compose
- Domain names pointing to your server:
  - `krc.bakersfieldesports.com` (Admin interface)
  - `kiosk.bakersfieldesports.com` (Kiosk interface)
- Ports 80 and 443 open for HTTP/HTTPS traffic

### Deployment Steps

1. **Prepare environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Configure external services**
   - Set up Zapier webhook URL and HMAC secret
   - Configure ggLeap API credentials (if using)
   - Set up proper database and Redis URLs

3. **Deploy**
   ```bash
   make deploy-prod
   ```

4. **Verify deployment**
   - Check https://krc.bakersfieldesports.com
   - Check https://kiosk.bakersfieldesports.com
   - Verify SSL certificates are issued

### Environment Variables

Key production environment variables:

```bash
# Application
APP_ENV=production
SECRET_KEY=your-secure-secret-key
TZ=America/Los_Angeles

# Database & Redis
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0

# Security
JWT_SECRET_KEY=your-jwt-secret
CORS_ORIGINS=https://krc.bakersfieldesports.com,https://kiosk.bakersfieldesports.com

# Integrations
ZAPIER_CATCH_HOOK_URL=https://hooks.zapier.com/hooks/catch/your-id/
ZAPIER_HMAC_SECRET=your-hmac-secret
TEXTLA_SENDER=+18668849961
GGLEAP_API_KEY=your-ggleap-key

# Features
FEATURE_MESSAGING=true
FEATURE_GGLEAP_SYNC=true
```

## 📊 Database Schema

### Core Tables

- **`users`**: Authentication and authorization
- **`clients`**: Customer information and profiles
- **`memberships`**: Subscription tracking with computed status
- **`check_ins`**: Visit history with method and station tracking
- **`contact_methods`**: Multi-channel communication preferences
- **`consents`**: GDPR-compliant consent management
- **`tags`**: Flexible client categorization
- **`webhooks_out`**: Zapier integration tracking with retry logic
- **`ggleap_links`**: Gaming center system integration
- **`audit_log`**: Complete change tracking

### Key Features

- **Computed Membership Status**: Automatically calculated as `active`, `expired`, or `pending`
- **Flexible External IDs**: JSONB field for integration with other systems
- **Comprehensive Indexing**: Optimized for search and reporting queries
- **Audit Trail**: Complete change tracking for compliance

## 🔧 Configuration

### Module System

Features are controlled via `config/modules.yaml`:

```yaml
modules:
  messaging:
    enabled: true
    features:
      zapier_webhooks: true
      sms_notifications: true

  ggleap:
    enabled: false  # Disabled in development
    features:
      group_sync: true
      auto_sync_on_status_change: true
```

### Scheduled Jobs

The worker system handles automated tasks:

- **Daily 9 AM**: Check for expiring memberships (30-day notice)
- **Monthly 15th**: Remind inactive members to check in
- **2nd Tuesday**: KRC meetup announcements
- **Nightly**: ggLeap group synchronization
- **Hourly**: Retry failed webhook deliveries

### Message Templates

Customizable message templates for automation:

```python
MESSAGE_TEMPLATES = {
    'welcome_sms': "Welcome to Bakersfield eSports Center! Your membership is now active.",
    'expiry_reminder': "Hi {name}! Your BEC membership expires on {expires_on}. Renew now!",
    'checkin_reminder': "Hi {name}! We miss you at BEC. Come by and check in!",
    'meetup_announcement': "Join us for the monthly KRC meetup at BEC!"
}
```

## 🧪 Testing

### Test Categories

- **Unit Tests**: Business logic and utility functions
- **Integration Tests**: API endpoints and database operations
- **End-to-End Tests**: Complete user workflows (especially kiosk)

### Running Tests

```bash
# All tests
make test

# Specific categories
make test-unit
make test-integration
make test-e2e

# With coverage
make test-coverage
```

### Key Test Scenarios

- **Authentication**: Login, token refresh, role-based access, forced password change
- **Client Management**: CRUD operations, search, tagging
- **Membership Logic**: Status calculation, expiration detection
- **Kiosk Flow**: Phone lookup, check-in process, error handling
- **Messaging**: Webhook signing, retry logic, template formatting
- **User Management**: Account creation with temporary passwords, password strength validation

## 🔒 Security

### Authentication & Authorization
- **JWT tokens** with refresh capability
- **Bcrypt password hashing** with secure rounds
- **Role-based access control** (admin/staff)
- **Protected endpoints** with dependency injection
- **Forced password change** on first login for new users
- **Strong password requirements** (12+ chars, uppercase, lowercase, digits, special chars)

### Data Protection
- **HTTPS everywhere** in production (Let's Encrypt)
- **CORS configuration** for trusted origins
- **SQL injection protection** via SQLAlchemy ORM
- **Input validation** with Pydantic schemas

### Webhook Security
- **HMAC-SHA256 signatures** for Zapier integration
- **Retry logic with exponential backoff**
- **Dead letter queue** for failed deliveries

## 📈 Monitoring & Maintenance

### Health Checks
- API endpoint: `/api/v1/healthz`
- Docker health checks for all services
- Database connection monitoring

### Backups
```bash
# Create backup
make backup

# Named backup
make backup-name NAME="pre-upgrade"

# List backups
make list-backups

# Restore
make restore BACKUP="backup_file.sql.gz"
```

### Log Access
```bash
# All services
make logs

# Specific service
make logs-api
make logs-worker
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `make test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Follow existing code patterns and module structure
- Add tests for new functionality
- Update documentation for API changes
- Use descriptive commit messages
- Ensure Docker builds pass

## 📄 License

This project is proprietary software developed for Bakersfield eSports Center.

## 🆘 Support

For technical support or questions:

1. Check the logs: `make logs`
2. Review health status: `make health`
3. Consult API documentation: http://localhost:8000/docs
4. Open an issue in the repository

### Common Troubleshooting

**Services won't start:**
```bash
make down
make clean
make dev
```

**Database connection issues:**
```bash
make shell-db  # Test direct connection
make migrate   # Ensure schema is up to date
```

**Kiosk not finding clients:**
- Check phone number format (10 digits)
- Verify client exists in database
- Review API logs for lookup errors

**Messages not sending:**
- Check `ZAPIER_MODE=production` in .env
- Verify webhook URL and HMAC secret
- Review worker logs: `make logs-worker`

---

Built with ❤️ for the gaming community at Bakersfield eSports Center