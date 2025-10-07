# Version Control & Release Process

This document describes the versioning strategy and release process for the BEC CRM system.

---

## Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

Example: 1.2.3
  │   │   └─ Patch: Bug fixes, backwards-compatible
  │   └───── Minor: New features, backwards-compatible
  └───────── Major: Breaking changes, incompatible API changes
```

### Version Number Guidelines

**MAJOR version (X.0.0)** - Increment when:
- Making incompatible API changes
- Removing features
- Changing database schema in non-backwards-compatible way
- Restructuring project architecture
- **Example:** v1.0.0 → v2.0.0

**MINOR version (0.X.0)** - Increment when:
- Adding new features (backwards-compatible)
- Adding new API endpoints
- Adding new database tables/columns (with migration)
- Deprecating features (but not removing)
- **Example:** v1.0.0 → v1.1.0

**PATCH version (0.0.X)** - Increment when:
- Bug fixes
- Performance improvements
- Documentation updates
- Security patches (non-breaking)
- Minor UI improvements
- **Example:** v1.0.0 → v1.0.1

---

## Current Version

**Version:** `1.0.0`
**Release Date:** 2025-10-03
**Status:** Production Ready

See [VERSION](./VERSION) file for current version number.

---

## Release Process

### 1. Development Phase

1. **Create feature branch**
   ```bash
   git checkout -b feature/add-reporting-module
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Update CHANGELOG.md**
   - Add changes to `[Unreleased]` section
   - Use appropriate category (Added, Changed, Fixed, etc.)

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add reporting module with PDF export"
   ```

### 2. Pre-Release Checklist

- [ ] All tests pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Database migrations tested (if applicable)
- [ ] Security review completed
- [ ] Breaking changes documented

### 3. Version Bump

**Determine new version number** based on changes:

**For Bug Fix (Patch):**
```bash
# Update VERSION file: 1.0.0 → 1.0.1
echo "1.0.1" > VERSION
```

**For New Feature (Minor):**
```bash
# Update VERSION file: 1.0.0 → 1.1.0
echo "1.1.0" > VERSION
```

**For Breaking Change (Major):**
```bash
# Update VERSION file: 1.0.0 → 2.0.0
echo "2.0.0" > VERSION
```

### 4. Update CHANGELOG.md

Move unreleased changes to new version section:

```markdown
## [Unreleased]

### Planned
- Future features...

---

## [1.1.0] - 2025-10-15

### Added
- Reporting module with PDF export
- Dashboard analytics
- Export to Excel functionality

### Fixed
- Client search performance issue
- Check-in duplicate prevention
```

### 5. Update API Version (if needed)

If making breaking API changes, update API version in:

```python
# apps/api/main.py
app = FastAPI(
    title=settings.API_TITLE,
    version="v2",  # Update this
    ...
)
```

### 6. Create Release Commit

```bash
git add VERSION CHANGELOG.md
git commit -m "chore: release v1.1.0"
```

### 7. Create Git Tag

```bash
git tag -a v1.1.0 -m "Release v1.1.0: Reporting Module

- Added PDF report generation
- Added dashboard analytics
- Fixed search performance issue

See CHANGELOG.md for full details."
```

### 8. Push to Repository

```bash
git push origin main
git push origin v1.1.0
```

### 9. Create GitHub Release (if using GitHub)

1. Go to repository → Releases → New Release
2. Choose tag: v1.1.0
3. Release title: "v1.1.0 - Reporting Module"
4. Description: Copy relevant section from CHANGELOG.md
5. Attach binary/artifacts if needed
6. Publish release

### 10. Deploy to Production

Follow [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) deployment steps.

### 11. Verify Deployment

```bash
# Check API version
curl https://krc.bec.local/api/v1/

# Check health
curl https://krc.bec.local/api/v1/healthz

# Verify in UI (footer should show version)
```

---

## Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature (→ MINOR version)
- `fix`: Bug fix (→ PATCH version)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `security`: Security fixes (→ PATCH version, urgent)
- `breaking`: Breaking changes (→ MAJOR version)

### Examples

```bash
# New feature
git commit -m "feat(clients): add bulk export to PDF"

# Bug fix
git commit -m "fix(auth): prevent duplicate login attempts"

# Breaking change
git commit -m "breaking(api): restructure client endpoints

BREAKING CHANGE: Client API endpoints moved from /clients to /api/v2/clients
Migration guide available in docs/migration-v2.md"

# Security fix
git commit -m "security(auth): patch JWT token validation vulnerability"

# Documentation
git commit -m "docs: update installation guide with HTTPS setup"
```

---

## Branching Strategy

### Main Branches

- `main` - Production-ready code, always deployable
- `develop` - Integration branch for features (optional)

### Supporting Branches

- `feature/*` - New features
  - Example: `feature/add-reporting`
  - Merge to: `main` or `develop`

- `fix/*` - Bug fixes
  - Example: `fix/login-validation`
  - Merge to: `main`

- `hotfix/*` - Urgent production fixes
  - Example: `hotfix/security-patch`
  - Merge to: `main`
  - Tag immediately

- `release/*` - Release preparation
  - Example: `release/v1.1.0`
  - For final testing before release

### Workflow

```
feature/add-reporting → main → v1.1.0 tag → deploy
fix/login-validation  → main → v1.0.1 tag → deploy
hotfix/security-patch → main → v1.0.2 tag → deploy (urgent)
```

---

## Database Migration Versioning

Database migrations are numbered sequentially:

```
001_initial_schema.py
002_add_notes_and_language.py
003_add_reporting_tables.py
```

### Creating New Migration

```bash
# Auto-generate migration
docker compose exec api alembic revision --autogenerate -m "add_reporting_tables"

# Edit the generated file to ensure correctness
# Test migration up
docker compose exec api alembic upgrade head

# Test migration down
docker compose exec api alembic downgrade -1

# Test migration up again
docker compose exec api alembic upgrade head
```

### Migration in CHANGELOG

```markdown
### Database Migrations
- **Migration 003**: Reporting tables (2025-10-15)
  - Added `reports` table
  - Added `report_schedules` table
  - Indexed for performance
```

---

## Rollback Procedure

### If deployment fails:

1. **Rollback code**
   ```bash
   git revert <commit-hash>
   # OR
   git reset --hard v1.0.0
   git push --force origin main
   ```

2. **Rollback database** (if migration was run)
   ```bash
   docker compose exec api alembic downgrade <previous-version>
   # Example: downgrade from 003 to 002
   docker compose exec api alembic downgrade 002
   ```

3. **Restore from backup** (if needed)
   ```bash
   gunzip < backup_20251003.sql.gz | docker compose exec -T postgres psql -U crm_user -d crm_db
   ```

4. **Redeploy previous version**
   ```bash
   git checkout v1.0.0
   docker compose down
   docker compose up -d
   ```

---

## Version Checking

### In Code

**Backend (Python):**
```python
# apps/api/main.py
VERSION = open("VERSION").read().strip()

@app.get("/")
async def root():
    return {
        "version": VERSION,
        "name": "BEC CRM API"
    }
```

**Frontend (TypeScript):**
```typescript
// vite.config.ts
import { readFileSync } from 'fs'
const version = readFileSync('./VERSION', 'utf-8').trim()

export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(version)
  }
})

// In component:
console.log(__APP_VERSION__) // "1.0.0"
```

### In UI

Add version to footer:
```typescript
// App.tsx
const version = __APP_VERSION__

<footer>
  BEC CRM v{version}
</footer>
```

---

## Changelog Automation (Future)

Consider tools for automating changelog generation:

- **conventional-changelog**: Generates changelog from commit messages
- **semantic-release**: Automates versioning and releases
- **GitHub Actions**: Automate release process

Example GitHub Action (`.github/workflows/release.yml`):
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
```

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-10-03 | Initial production release |

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)

---

**Maintained by:** BEC Development Team
**Last Updated:** 2025-10-03
