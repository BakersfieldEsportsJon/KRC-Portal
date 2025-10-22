#!/bin/bash
# Create a versioned release package for production deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}KRC CRM Release Packager${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Get version from VERSION file or prompt
if [ -f VERSION ]; then
    CURRENT_VERSION=$(cat VERSION)
    echo -e "${YELLOW}Current version: ${CURRENT_VERSION}${NC}"
    read -p "New version (press Enter to keep ${CURRENT_VERSION}): " NEW_VERSION
    VERSION=${NEW_VERSION:-$CURRENT_VERSION}
else
    read -p "Version number (e.g., 1.0.0): " VERSION
fi

# Update VERSION file
echo "$VERSION" > VERSION

# Create release directory
RELEASE_NAME="krc-crm-v${VERSION}"
RELEASE_DIR="releases/${RELEASE_NAME}"
ARCHIVE_NAME="${RELEASE_NAME}.tar.gz"

echo ""
echo -e "${GREEN}Creating release: ${RELEASE_NAME}${NC}"
echo ""

# Clean old release if exists
if [ -d "$RELEASE_DIR" ]; then
    echo -e "${YELLOW}Removing old release directory...${NC}"
    rm -rf "$RELEASE_DIR"
fi

# Create release directory structure
mkdir -p "$RELEASE_DIR"

echo "📦 Packaging files..."

# Copy application files
cp -r apps "$RELEASE_DIR/"
cp -r modules "$RELEASE_DIR/"
cp -r scripts "$RELEASE_DIR/"
cp -r infra "$RELEASE_DIR/"
cp -r docs "$RELEASE_DIR/"

# Copy configuration files
cp docker-compose.prod.yml "$RELEASE_DIR/docker-compose.yml"
cp .env.production.example "$RELEASE_DIR/.env.example"
cp .gitignore "$RELEASE_DIR/"
cp VERSION "$RELEASE_DIR/"

# Copy documentation
cp README.md "$RELEASE_DIR/" 2>/dev/null || echo "README not found, skipping"
cp DEPLOYMENT_INSTRUCTIONS.md "$RELEASE_DIR/" 2>/dev/null || echo "DEPLOYMENT_INSTRUCTIONS not found, skipping"
cp ENVIRONMENT_SETUP.md "$RELEASE_DIR/" 2>/dev/null || echo "ENVIRONMENT_SETUP not found, skipping"
cp UPDATE_STRATEGY.md "$RELEASE_DIR/" 2>/dev/null || echo "UPDATE_STRATEGY not found, skipping"
cp QUICK_REFERENCE.md "$RELEASE_DIR/" 2>/dev/null || echo "QUICK_REFERENCE not found, skipping"

# Create installation script
cat > "$RELEASE_DIR/install.sh" << 'EOF'
#!/bin/bash
# KRC CRM Production Installation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}KRC CRM Production Installer${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file with your production settings!${NC}"
        echo -e "${YELLOW}   - Set strong passwords${NC}"
        echo -e "${YELLOW}   - Configure API keys${NC}"
        echo -e "${YELLOW}   - Set production URLs${NC}"
        echo ""
        read -p "Press Enter after you've edited .env, or Ctrl+C to exit..."
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo -e "${BLUE}Building and starting services...${NC}"
echo ""

# Build and start services
docker-compose up -d --build

echo ""
echo -e "${BLUE}Waiting for services to be healthy...${NC}"
sleep 10

# Check status
docker-compose ps

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Access your CRM at: ${BLUE}http://localhost${NC}"
echo -e "API documentation: ${BLUE}http://localhost/api/docs${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Create an admin user:"
echo -e "   ${BLUE}docker-compose exec api python -m scripts.create_admin${NC}"
echo ""
echo "2. Check logs:"
echo -e "   ${BLUE}docker-compose logs -f${NC}"
echo ""
echo "3. Read UPDATE_STRATEGY.md for how to update safely"
echo ""

EOF

chmod +x "$RELEASE_DIR/install.sh"

# Create update script
cat > "$RELEASE_DIR/update.sh" << 'EOF'
#!/bin/bash
# KRC CRM Production Update Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}KRC CRM Update${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if already installed
if [ ! -f .env ]; then
    echo -e "${RED}Error: No .env file found. Run install.sh first.${NC}"
    exit 1
fi

# Backup database
echo -e "${YELLOW}Creating backup...${NC}"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec -T postgres pg_dump -U crm_prod_user crm_prod > "$BACKUP_FILE"
gzip "$BACKUP_FILE"
echo -e "${GREEN}✓ Backup created: ${BACKUP_FILE}.gz${NC}"
echo ""

# Update services
echo -e "${BLUE}Updating services...${NC}"
docker-compose up -d --build

echo ""
echo -e "${BLUE}Waiting for services to restart...${NC}"
sleep 10

# Check status
docker-compose ps

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Update Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Backup saved to: ${BLUE}${BACKUP_FILE}.gz${NC}"
echo ""

EOF

chmod +x "$RELEASE_DIR/update.sh"

# Create README for the release
cat > "$RELEASE_DIR/RELEASE_README.md" << EOF
# KRC Gaming Center CRM - Version ${VERSION}

## Production Release Package

This is a complete, ready-to-deploy package for the KRC Gaming Center CRM system.

## Quick Start

### 1. Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- At least 2GB RAM available
- 10GB disk space

### 2. Installation

\`\`\`bash
# Extract the package
tar -xzf ${ARCHIVE_NAME}
cd ${RELEASE_NAME}

# Run the installer
./install.sh
\`\`\`

The installer will:
- Check prerequisites
- Create .env file from template
- Build Docker containers
- Start all services

### 3. Initial Setup

After installation:

\`\`\`bash
# Create admin user
docker-compose exec api python -m scripts.create_admin

# View logs
docker-compose logs -f
\`\`\`

Access the application at: http://localhost

## What's Included

- **apps/** - Application code (API, Web, Worker)
- **modules/** - Modular features
- **scripts/** - Utility scripts
- **infra/** - Infrastructure configuration
- **docs/** - Complete documentation
- **docker-compose.yml** - Production configuration
- **install.sh** - Automated installer
- **update.sh** - Update script with automatic backup

## Documentation

- **DEPLOYMENT_INSTRUCTIONS.md** - Full deployment guide
- **ENVIRONMENT_SETUP.md** - Environment management
- **UPDATE_STRATEGY.md** - Safe update procedures
- **QUICK_REFERENCE.md** - Command reference

## Updating

To update to a newer version:

\`\`\`bash
# Stop current version
docker-compose down

# Extract new version over current directory
tar -xzf krc-crm-v<new-version>.tar.gz --strip-components=1

# Run update script (automatically backs up database)
./update.sh
\`\`\`

## Support

For issues or questions:
- Check docs/ folder for detailed guides
- Review logs: \`docker-compose logs\`
- GitHub: [Your repository URL]

## Version Information

- Version: ${VERSION}
- Release Date: $(date +%Y-%m-%d)
- Docker Compose: Production configuration included
- Database: PostgreSQL 16
- Redis: Version 7
- Web Server: Caddy 2

## Security Notes

- Change all default passwords in .env
- Use strong JWT secrets
- Configure SSL/TLS for production domains
- Review CORS settings
- Enable firewall rules

## System Requirements

**Minimum:**
- 2 CPU cores
- 2GB RAM
- 10GB disk space

**Recommended:**
- 4 CPU cores
- 4GB RAM
- 50GB disk space (for logs and backups)

EOF

# Create version info file
cat > "$RELEASE_DIR/VERSION_INFO.txt" << EOF
KRC Gaming Center CRM
Version: ${VERSION}
Release Date: $(date +%Y-%m-%d %H:%M:%S)
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Git Branch: $(git branch --show-current 2>/dev/null || echo "N/A")

Build Information:
- Built on: $(date)
- Built by: $(whoami)
- System: $(uname -s)

Included Components:
- FastAPI Backend
- React Frontend
- PostgreSQL 16
- Redis 7
- Caddy Web Server
- Background Workers
- Task Scheduler

EOF

# Create checksums
echo "🔐 Generating checksums..."
cd "$RELEASE_DIR"
find . -type f -exec sha256sum {} \; > CHECKSUMS.txt
cd - > /dev/null

# Create archive
echo "📦 Creating archive..."
cd releases
tar -czf "$ARCHIVE_NAME" "$RELEASE_NAME"
cd - > /dev/null

# Calculate final checksum
ARCHIVE_CHECKSUM=$(sha256sum "releases/$ARCHIVE_NAME" | cut -d' ' -f1)

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Release Created Successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Version: ${BLUE}${VERSION}${NC}"
echo -e "Package: ${BLUE}releases/${ARCHIVE_NAME}${NC}"
echo -e "Size: ${BLUE}$(du -h "releases/$ARCHIVE_NAME" | cut -f1)${NC}"
echo -e "SHA256: ${BLUE}${ARCHIVE_CHECKSUM}${NC}"
echo ""
echo -e "${YELLOW}Release package includes:${NC}"
echo "  ✓ All application code"
echo "  ✓ Docker configuration"
echo "  ✓ Installation script"
echo "  ✓ Update script (with auto-backup)"
echo "  ✓ Complete documentation"
echo "  ✓ Version information"
echo ""
echo -e "${YELLOW}To deploy:${NC}"
echo -e "  1. Copy ${BLUE}releases/${ARCHIVE_NAME}${NC} to production server"
echo -e "  2. Extract: ${BLUE}tar -xzf ${ARCHIVE_NAME}${NC}"
echo -e "  3. Run: ${BLUE}cd ${RELEASE_NAME} && ./install.sh${NC}"
echo ""
echo -e "${YELLOW}To create a git tag:${NC}"
echo -e "  ${BLUE}git tag -a v${VERSION} -m 'Release version ${VERSION}'${NC}"
echo -e "  ${BLUE}git push origin v${VERSION}${NC}"
echo ""

# Update latest symlink
cd releases
ln -sf "$ARCHIVE_NAME" "krc-crm-latest.tar.gz"
cd - > /dev/null

echo -e "${GREEN}✓ Latest release symlink updated${NC}"
echo ""
