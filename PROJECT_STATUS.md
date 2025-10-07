# CRM Project Status

## Last Updated
2025-10-06

## Important Development Guidelines

### ⚠️ CRITICAL: Version Control Policy
**ALWAYS commit changes to git before making modifications to any file.**

Before making any changes:
1. Run `git status` to check current state
2. Run `git add -A && git commit -m "descriptive message"` to save current state
3. Make your changes
4. Test thoroughly
5. Commit again with descriptive message

This ensures we can always revert to a working state if changes cause issues.

## Current Status

### ✅ Completed Features

1. **Version Control Setup**
   - Git repository initialized
   - .gitignore configured for Node.js, Python, Docker, and database files
   - All changes tracked with descriptive commits

2. **Client Management Enhancements**
   - Check-in buttons on both client list and detail pages
   - Color-coded status indicators (Active=green, Expiring=yellow, Expired=red)
   - Membership status display with expiration dates
   - 30-day expiration warning threshold
   - Last check-in display with timestamp and location
   - 30-day inactivity warning banner

3. **Dashboard Statistics**
   - Fixed timezone handling (America/Los_Angeles)
   - Accurate check-in counters (today, this week, this month)
   - Unique client counts
   - Popular stations tracking

4. **UI/UX Improvements**
   - Fixed modal overflow issues with scrollable content
   - 2-column grid layout for client forms
   - Responsive design improvements

5. **Staff Notes Feature**
   - Timestamped notes with user attribution
   - Notes section on client detail page
   - Full audit trail of who created each note

6. **User Management**
   - Admin can create staff accounts
   - Fixed timestamp constraint violations
   - Fixed password hashing scheme mismatch (bcrypt)
   - Staff login now working correctly

### 🔧 Technical Details

**Backend (FastAPI + Python)**
- Async/await patterns throughout
- SQLAlchemy ORM with async sessions
- PostgreSQL database with timezone-aware timestamps
- Bcrypt password hashing (passlib)
- JWT authentication
- CORS configured for cross-origin requests

**Frontend (React + TypeScript)**
- Vite for development and building
- React Query for data fetching
- Tailwind CSS for styling
- Hot module reloading

**Infrastructure**
- Docker Compose for local development
- PostgreSQL database container
- Separate API and web containers

### 📁 Key Files

- `apps/api/auth_workaround.py` - Authentication endpoints (bcrypt hashing)
- `apps/api/users_api.py` - User management (admin only, bcrypt hashing)
- `apps/api/clients_api.py` - Client CRUD and notes
- `apps/api/checkins_api.py` - Check-in management and statistics
- `apps/api/models.py` - Central SQLAlchemy models
- `apps/web/src/pages/ClientDetailPage.tsx` - Enhanced client details
- `apps/web/src/pages/ClientsPage.tsx` - Client list with check-ins
- `apps/web/src/services/api.ts` - API service client

### 🐛 Known Issues
None currently

### 📝 Recent Fixes

1. **Login Authentication Issue** (2025-10-06)
   - Problem: Staff accounts couldn't log in - "hash could not be identified" error
   - Cause: auth_workaround.py used argon2 while users_api.py used bcrypt
   - Solution: Changed both to use bcrypt consistently
   - Commit: f20ea5a

2. **User Creation Timestamp Error** (Previous)
   - Problem: Null constraint violation on created_at/updated_at
   - Solution: Explicitly set timestamps in user creation

3. **Timezone Statistics Issue** (Previous)
   - Problem: Check-in counters showing 0
   - Solution: Use pytz to handle America/Los_Angeles timezone correctly

4. **Modal Overflow** (Previous)
   - Problem: Add client modal extended past viewport
   - Solution: Added max-height, scrollable content, 2-column grid

### 🎯 Development Workflow

1. Always commit before changes
2. Test in local environment (http://localhost:3000)
3. Check Docker logs if issues: `docker-compose logs -f api`
4. Restart services if needed: `docker-compose restart api`
5. Commit working changes with descriptive messages

### 🔐 Test Accounts

- Admin: admin@bakersfieldesports.com
- Staff: staff@bakersfieldesports.com / staff123

### 🚀 Starting the Application

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart api
docker-compose restart web

# Stop all services
docker-compose down
```

### 📊 Git Commit History

All commits follow convention:
- Clear, descriptive subject line
- Detailed explanation of changes
- Lists specific fixes/features
- Includes Claude Code attribution
