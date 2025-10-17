# Release Guide - Creating Production Packages

## Overview

This guide explains how to create versioned, self-contained release packages that can be deployed to production servers.

## What is a Release Package?

A release package is a complete, ready-to-deploy bundle containing:
- All application code (API, Web, Worker)
- Production Docker configuration
- Installation script (automated setup)
- Update script (with automatic backups)
- Complete documentation
- Version information

## Creating a Release

### On Windows:

```cmd
cd scripts
create-release.bat
```

### On Linux/Mac:

```bash
cd scripts
chmod +x create-release.sh
./create-release.sh
```

### What Happens:

1. **Prompts for version number** (e.g., 1.0.0, 1.1.0, 2.0.0)
2. **Creates release directory** with all necessary files
3. **Generates installation scripts** for easy deployment
4. **Creates compressed archive** (.zip for Windows, .tar.gz for Linux)
5. **Generates checksums** for integrity verification
6. **Updates VERSION file** in repository

## Release Package Contents

```
krc-crm-v1.0.0/
├── apps/                          # Application code
│   ├── api/                       # Backend API
│   ├── web/                       # Frontend
│   └── worker/                    # Background workers
├── modules/                       # Feature modules
├── scripts/                       # Utility scripts
├── infra/                         # Infrastructure configs
├── docs/                          # Documentation
├── docker-compose.yml             # Production config
├── .env.example                   # Environment template
├── install.bat / install.sh       # Automated installer
├── update.bat / update.sh         # Update script
├── RELEASE_README.md              # Release notes
├── VERSION_INFO.txt               # Build information
├── CHECKSUMS.txt                  # File integrity
└── [Documentation files]          # Setup guides
```

## Version Numbering

We follow Semantic Versioning (SemVer): **MAJOR.MINOR.PATCH**

### MAJOR version (X.0.0)
- Breaking changes
- Major feature overhauls
- Database schema changes requiring migration
- API changes that break backwards compatibility

**Example:** 1.0.0 → 2.0.0

### MINOR version (1.X.0)
- New features
- Non-breaking enhancements
- New modules added
- Performance improvements

**Example:** 1.0.0 → 1.1.0

### PATCH version (1.0.X)
- Bug fixes
- Security patches
- Minor tweaks
- Documentation updates

**Example:** 1.0.0 → 1.0.1

## Release Workflow

### 1. Prepare for Release

```bash
# Make sure all changes are committed
git status

# Make sure tests pass (if you have them)
docker-compose -f docker-compose.dev.yml exec api pytest

# Update documentation
# - CHANGELOG.md (if you have one)
# - README.md
# - Version-specific notes
```

### 2. Create the Release

```bash
# Run the release script
cd scripts
./create-release.sh  # or create-release.bat on Windows

# Enter version when prompted (e.g., 1.0.0)
```

### 3. Test the Release Package

```bash
# Extract to a test location
cd /tmp
tar -xzf /path/to/krc-crm-v1.0.0.tar.gz
cd krc-crm-v1.0.0

# Test installation
./install.sh

# Verify it works
docker-compose ps
curl http://localhost/api/v1/healthz
```

### 4. Tag in Git

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to remote
git push origin v1.0.0

# Push code
git push origin main
```

### 5. Distribute the Release

The release package is in `releases/` directory:
- **Windows**: `krc-crm-v1.0.0.zip`
- **Linux/Mac**: `krc-crm-v1.0.0.tar.gz`

Share this file with:
- Production servers
- Deployment team
- Customer installations
- Backup archives

## Deploying a Release

### On Production Server:

**Windows:**
```cmd
# 1. Extract ZIP file
# 2. Open folder in terminal
cd krc-crm-v1.0.0

# 3. Edit .env file
copy .env.example .env
notepad .env  # Set production values

# 4. Run installer
install.bat
```

**Linux/Mac:**
```bash
# 1. Extract archive
tar -xzf krc-crm-v1.0.0.tar.gz
cd krc-crm-v1.0.0

# 2. Edit .env file
cp .env.example .env
nano .env  # Set production values

# 3. Run installer
chmod +x install.sh
./install.sh
```

### After Installation:

```bash
# Create admin user
docker-compose exec api python -m scripts.create_admin

# Verify services
docker-compose ps

# Check logs
docker-compose logs -f
```

## Updating to a New Release

### Method 1: Using Update Script (Recommended)

**Windows:**
```cmd
# 1. Stop current version
docker-compose down

# 2. Extract new version to same folder
# (This will overwrite files but preserve .env and data)

# 3. Run update script (automatically backs up DB)
update.bat
```

**Linux/Mac:**
```bash
# 1. Stop current version
docker-compose down

# 2. Extract new version
tar -xzf krc-crm-v1.1.0.tar.gz --strip-components=1

# 3. Run update script (automatically backs up DB)
./update.sh
```

### Method 2: Manual Update

```bash
# 1. Backup database
docker-compose exec postgres pg_dump -U crm_prod_user crm_prod > backup.sql

# 2. Stop services
docker-compose down

# 3. Extract new version
tar -xzf krc-crm-v1.1.0.tar.gz --strip-components=1

# 4. Rebuild and start
docker-compose up -d --build

# 5. Verify
docker-compose ps
```

## Release Checklist

Before creating a production release:

- [ ] All features tested in development
- [ ] No known critical bugs
- [ ] Documentation updated
- [ ] VERSION file updated
- [ ] .env.production.example has all required variables
- [ ] Database migrations tested (if any)
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Backup/restore procedures verified
- [ ] Rollback plan documented

## Managing Multiple Releases

### Directory Structure

```
releases/
├── krc-crm-v1.0.0.tar.gz
├── krc-crm-v1.0.1.tar.gz
├── krc-crm-v1.1.0.tar.gz
├── krc-crm-v2.0.0.tar.gz
└── krc-crm-latest.tar.gz  # Symlink to latest
```

### Keeping Old Releases

Keep old releases for:
- Rollback scenarios
- Historical reference
- Customer support
- Compliance/audit

Recommend keeping:
- All major versions
- Last 3 minor versions
- Last 5 patch versions

## Automating Releases

### Using Git Tags

```bash
# Create release from a tag
git checkout v1.0.0
./scripts/create-release.sh
```

### CI/CD Integration (Future)

You can integrate with GitHub Actions, GitLab CI, etc:

```yaml
# Example GitHub Actions workflow
name: Create Release
on:
  push:
    tags:
      - 'v*'
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create Release Package
        run: ./scripts/create-release.sh
      - name: Upload Release
        uses: actions/upload-artifact@v2
        with:
          name: release-package
          path: releases/*.tar.gz
```

## Troubleshooting

### Issue: "Version already exists"

```bash
# Remove old release first
rm -rf releases/krc-crm-v1.0.0
rm releases/krc-crm-v1.0.0.tar.gz
```

### Issue: "Installation fails"

Check:
1. Docker is running
2. .env file is configured
3. Ports 80/443 are available
4. Sufficient disk space

### Issue: "Update doesn't work"

```bash
# Manual rollback
docker-compose down
tar -xzf old-version.tar.gz --strip-components=1
docker-compose up -d
```

## Best Practices

1. **Test Before Release**
   - Always test the release package on a clean system
   - Verify installation from scratch
   - Test update process

2. **Document Changes**
   - Keep a CHANGELOG.md
   - Document breaking changes
   - Include upgrade notes

3. **Version Consistently**
   - Follow SemVer strictly
   - Don't skip versions
   - Tag in Git

4. **Secure Releases**
   - Don't include .env files
   - Verify checksums
   - Sign releases (optional)

5. **Backup Strategy**
   - Always backup before updates
   - Test restore procedures
   - Keep multiple backup copies

## Example Release Timeline

### v1.0.0 - Initial Release
- Full CRM functionality
- User management
- Client tracking
- Membership system

### v1.0.1 - Bug Fix Release
- Fixed dark mode toggle notification
- Fixed username update email preservation
- Security: Password reset URL logging removed

### v1.1.0 - Feature Release
- Added client notes feature
- Enhanced reporting
- New dashboard widgets
- Performance improvements

### v2.0.0 - Major Release
- Complete UI redesign
- New API endpoints
- Database schema changes
- Breaking: Old API deprecated

## Support and Maintenance

- **Security updates**: Released as PATCH versions
- **Bug fixes**: Released as PATCH versions
- **New features**: Released as MINOR versions
- **Major changes**: Released as MAJOR versions

## Questions?

Refer to:
- **UPDATE_STRATEGY.md** - Safe update procedures
- **DEPLOYMENT_INSTRUCTIONS.md** - Deployment guide
- **ENVIRONMENT_SETUP.md** - Environment management
