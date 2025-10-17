@echo off
REM Create a versioned release package for production deployment (Windows version)

setlocal enabledelayedexpansion

echo ================================
echo KRC CRM Release Packager
echo ================================
echo.

REM Get version from VERSION file or prompt
if exist VERSION (
    set /p CURRENT_VERSION=<VERSION
    echo Current version: !CURRENT_VERSION!
    set /p NEW_VERSION=New version (press Enter to keep !CURRENT_VERSION!):
    if "!NEW_VERSION!"=="" (
        set VERSION=!CURRENT_VERSION!
    ) else (
        set VERSION=!NEW_VERSION!
    )
) else (
    set /p VERSION=Version number (e.g., 1.0.0):
)

REM Update VERSION file
echo !VERSION!> VERSION

REM Create release directory
set RELEASE_NAME=krc-crm-v!VERSION!
set RELEASE_DIR=releases\!RELEASE_NAME!
set ARCHIVE_NAME=!RELEASE_NAME!.zip

echo.
echo Creating release: !RELEASE_NAME!
echo.

REM Clean old release if exists
if exist "!RELEASE_DIR!" (
    echo Removing old release directory...
    rmdir /s /q "!RELEASE_DIR!"
)

REM Create release directory structure
mkdir "!RELEASE_DIR!"

echo Packaging files...

REM Copy application files
xcopy /E /I /Y apps "!RELEASE_DIR!\apps"
xcopy /E /I /Y modules "!RELEASE_DIR!\modules"
xcopy /E /I /Y scripts "!RELEASE_DIR!\scripts"
xcopy /E /I /Y infra "!RELEASE_DIR!\infra"
if exist docs xcopy /E /I /Y docs "!RELEASE_DIR!\docs"

REM Copy configuration files
copy docker-compose.prod.yml "!RELEASE_DIR!\docker-compose.yml"
copy .env.production.example "!RELEASE_DIR!\.env.example"
copy .gitignore "!RELEASE_DIR!\"
copy VERSION "!RELEASE_DIR!\"

REM Copy documentation
if exist README.md copy README.md "!RELEASE_DIR!\"
if exist DEPLOYMENT_INSTRUCTIONS.md copy DEPLOYMENT_INSTRUCTIONS.md "!RELEASE_DIR!\"
if exist ENVIRONMENT_SETUP.md copy ENVIRONMENT_SETUP.md "!RELEASE_DIR!\"
if exist UPDATE_STRATEGY.md copy UPDATE_STRATEGY.md "!RELEASE_DIR!\"
if exist QUICK_REFERENCE.md copy QUICK_REFERENCE.md "!RELEASE_DIR!\"

REM Create installation script for Windows
(
echo @echo off
echo REM KRC CRM Production Installation Script
echo.
echo echo ================================
echo echo KRC CRM Production Installer
echo echo ================================
echo echo.
echo.
echo REM Check if Docker is installed
echo where docker ^>nul 2^>nul
echo if errorlevel 1 ^(
echo     echo Error: Docker is not installed
echo     echo Please install Docker Desktop first: https://docs.docker.com/desktop/install/windows-install/
echo     exit /b 1
echo ^)
echo.
echo REM Check if Docker Compose is installed
echo where docker-compose ^>nul 2^>nul
echo if errorlevel 1 ^(
echo     echo Error: Docker Compose is not installed
echo     exit /b 1
echo ^)
echo.
echo echo [OK] Docker is installed
echo echo [OK] Docker Compose is installed
echo echo.
echo.
echo REM Check if .env exists
echo if not exist .env ^(
echo     echo Creating .env file from template...
echo     if exist .env.example ^(
echo         copy .env.example .env
echo         echo.
echo         echo WARNING: Edit .env file with your production settings!
echo         echo    - Set strong passwords
echo         echo    - Configure API keys
echo         echo    - Set production URLs
echo         echo.
echo         pause
echo     ^) else ^(
echo         echo Error: .env.example not found
echo         exit /b 1
echo     ^)
echo ^) else ^(
echo     echo [OK] .env file exists
echo ^)
echo.
echo echo.
echo echo Building and starting services...
echo echo.
echo.
echo REM Build and start services
echo docker-compose up -d --build
echo.
echo echo.
echo echo Waiting for services to be healthy...
echo timeout /t 10 /nobreak ^>nul
echo.
echo REM Check status
echo docker-compose ps
echo.
echo echo.
echo echo ================================
echo echo Installation Complete!
echo echo ================================
echo echo.
echo echo Access your CRM at: http://localhost
echo echo API documentation: http://localhost/api/docs
echo echo.
echo echo Next steps:
echo echo 1. Create an admin user:
echo echo    docker-compose exec api python -m scripts.create_admin
echo echo.
echo echo 2. Check logs:
echo echo    docker-compose logs -f
echo echo.
echo echo 3. Read UPDATE_STRATEGY.md for how to update safely
echo echo.
) > "!RELEASE_DIR!\install.bat"

REM Create update script for Windows
(
echo @echo off
echo REM KRC CRM Production Update Script
echo.
echo echo ================================
echo echo KRC CRM Update
echo echo ================================
echo echo.
echo.
echo REM Check if already installed
echo if not exist .env ^(
echo     echo Error: No .env file found. Run install.bat first.
echo     exit /b 1
echo ^)
echo.
echo REM Backup database
echo echo Creating backup...
echo set BACKUP_FILE=backup_%%date:~-4,4%%%%date:~-10,2%%%%date:~-7,2%%_%%time:~0,2%%%%time:~3,2%%%%time:~6,2%%.sql
echo docker-compose exec -T postgres pg_dump -U crm_prod_user crm_prod ^> %%BACKUP_FILE%%
echo powershell Compress-Archive -Path %%BACKUP_FILE%% -DestinationPath %%BACKUP_FILE%%.zip
echo del %%BACKUP_FILE%%
echo echo [OK] Backup created: %%BACKUP_FILE%%.zip
echo echo.
echo.
echo REM Update services
echo echo Updating services...
echo docker-compose up -d --build
echo.
echo echo.
echo echo Waiting for services to restart...
echo timeout /t 10 /nobreak ^>nul
echo.
echo REM Check status
echo docker-compose ps
echo.
echo echo.
echo echo ================================
echo echo Update Complete!
echo echo ================================
echo echo.
echo echo Backup saved to: %%BACKUP_FILE%%.zip
echo echo.
) > "!RELEASE_DIR!\update.bat"

REM Create README for the release
(
echo # KRC Gaming Center CRM - Version !VERSION!
echo.
echo ## Production Release Package
echo.
echo This is a complete, ready-to-deploy package for the KRC Gaming Center CRM system.
echo.
echo ## Quick Start
echo.
echo ### 1. Prerequisites
echo.
echo - Docker Desktop for Windows
echo - At least 2GB RAM available
echo - 10GB disk space
echo.
echo ### 2. Installation
echo.
echo ```
echo # Extract the ZIP file
echo # Open the extracted folder
echo # Run install.bat
echo ```
echo.
echo The installer will:
echo - Check prerequisites
echo - Create .env file from template
echo - Build Docker containers
echo - Start all services
echo.
echo ### 3. Initial Setup
echo.
echo After installation:
echo.
echo ```
echo # Create admin user
echo docker-compose exec api python -m scripts.create_admin
echo.
echo # View logs
echo docker-compose logs -f
echo ```
echo.
echo Access the application at: http://localhost
echo.
echo ## Updating
echo.
echo To update to a newer version:
echo.
echo 1. Stop current version: `docker-compose down`
echo 2. Extract new version ZIP to the same folder
echo 3. Run `update.bat` ^(automatically backs up database^)
echo.
echo ## Version Information
echo.
echo - Version: !VERSION!
echo - Release Date: %date%
echo.
) > "!RELEASE_DIR!\RELEASE_README.md"

REM Create version info file
(
echo KRC Gaming Center CRM
echo Version: !VERSION!
echo Release Date: %date% %time%
echo.
echo Build Information:
echo - Built on: %date% %time%
echo - Built by: %username%
echo - System: Windows
echo.
echo Included Components:
echo - FastAPI Backend
echo - React Frontend
echo - PostgreSQL 16
echo - Redis 7
echo - Caddy Web Server
echo - Background Workers
echo - Task Scheduler
echo.
) > "!RELEASE_DIR!\VERSION_INFO.txt"

REM Create archive (requires PowerShell)
echo Creating archive...
powershell Compress-Archive -Path "!RELEASE_DIR!" -DestinationPath "releases\!ARCHIVE_NAME!" -Force

REM Get file size
for %%A in ("releases\!ARCHIVE_NAME!") do set SIZE=%%~zA

echo.
echo ================================
echo Release Created Successfully!
echo ================================
echo.
echo Version: !VERSION!
echo Package: releases\!ARCHIVE_NAME!
echo Size: !SIZE! bytes
echo.
echo Release package includes:
echo   [OK] All application code
echo   [OK] Docker configuration
echo   [OK] Installation script ^(install.bat^)
echo   [OK] Update script ^(update.bat^)
echo   [OK] Complete documentation
echo   [OK] Version information
echo.
echo To deploy:
echo   1. Copy releases\!ARCHIVE_NAME! to production server
echo   2. Extract the ZIP file
echo   3. Run install.bat
echo.
echo To create a git tag:
echo   git tag -a v!VERSION! -m "Release version !VERSION!"
echo   git push origin v!VERSION!
echo.

endlocal
