#!/usr/bin/env python3
"""
Backup and restore utilities for BEC CRM system

Provides tools for:
- Creating database backups
- Restoring from backups
- Scheduled backup management
- Data migration utilities
"""

import sys
import os
import subprocess
import shutil
from datetime import datetime, timedelta
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BACKUP_DIR = Path("/backups")
RETENTION_DAYS = 30
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crm_user:crm_password@localhost:5432/crm_db")


def ensure_backup_directory():
    """Ensure backup directory exists"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Backup directory: {BACKUP_DIR}")


def parse_database_url(url: str) -> dict:
    """Parse database URL into components"""
    # Simple parsing for postgresql://user:pass@host:port/db
    if not url.startswith("postgresql://"):
        raise ValueError("Only PostgreSQL databases are supported")

    url = url.replace("postgresql://", "")
    if "@" in url:
        auth, host_db = url.split("@", 1)
        if ":" in auth:
            username, password = auth.split(":", 1)
        else:
            username, password = auth, ""
    else:
        username, password = "", ""
        host_db = url

    if "/" in host_db:
        host_port, database = host_db.rsplit("/", 1)
    else:
        host_port, database = host_db, ""

    if ":" in host_port:
        host, port = host_port.split(":", 1)
    else:
        host, port = host_port, "5432"

    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "database": database
    }


def create_backup(backup_name: str = None) -> Path:
    """Create a database backup using pg_dump"""
    ensure_backup_directory()

    if not backup_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"bec_crm_backup_{timestamp}"

    backup_file = BACKUP_DIR / f"{backup_name}.sql"

    try:
        db_config = parse_database_url(DATABASE_URL)

        # Set environment variables for pg_dump
        env = os.environ.copy()
        if db_config["password"]:
            env["PGPASSWORD"] = db_config["password"]

        # Build pg_dump command
        cmd = [
            "pg_dump",
            "-h", db_config["host"],
            "-p", db_config["port"],
            "-U", db_config["username"],
            "-d", db_config["database"],
            "--no-password",
            "--verbose",
            "--clean",
            "--if-exists",
            "--create",
            "-f", str(backup_file)
        ]

        logger.info(f"Creating backup: {backup_file}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode == 0:
            # Compress the backup
            compressed_file = backup_file.with_suffix('.sql.gz')
            subprocess.run(["gzip", str(backup_file)], check=True)

            logger.info(f"✅ Backup created successfully: {compressed_file}")
            return compressed_file
        else:
            logger.error(f"❌ Backup failed: {result.stderr}")
            raise Exception(f"pg_dump failed: {result.stderr}")

    except Exception as e:
        logger.error(f"❌ Error creating backup: {e}")
        if backup_file.exists():
            backup_file.unlink()
        raise


def restore_backup(backup_file: Path, target_db: str = None) -> bool:
    """Restore database from backup file"""
    if not backup_file.exists():
        logger.error(f"❌ Backup file not found: {backup_file}")
        return False

    try:
        db_config = parse_database_url(DATABASE_URL)
        if target_db:
            db_config["database"] = target_db

        # Decompress if needed
        sql_file = backup_file
        if backup_file.suffix == '.gz':
            sql_file = backup_file.with_suffix('')
            logger.info(f"Decompressing backup: {backup_file}")
            subprocess.run(["gunzip", "-c", str(backup_file)],
                         stdout=open(sql_file, 'w'), check=True)

        # Set environment variables for psql
        env = os.environ.copy()
        if db_config["password"]:
            env["PGPASSWORD"] = db_config["password"]

        # Build psql command
        cmd = [
            "psql",
            "-h", db_config["host"],
            "-p", db_config["port"],
            "-U", db_config["username"],
            "-d", "postgres",  # Connect to postgres db first
            "--no-password",
            "-f", str(sql_file)
        ]

        logger.info(f"Restoring backup: {backup_file}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        # Clean up decompressed file if we created it
        if backup_file.suffix == '.gz' and sql_file.exists():
            sql_file.unlink()

        if result.returncode == 0:
            logger.info("✅ Backup restored successfully")
            return True
        else:
            logger.error(f"❌ Restore failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Error restoring backup: {e}")
        return False


def list_backups() -> list:
    """List available backup files"""
    ensure_backup_directory()

    backups = []
    for file in BACKUP_DIR.glob("*.sql.gz"):
        stat = file.stat()
        backups.append({
            "file": file,
            "name": file.stem.replace(".sql", ""),
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_mtime)
        })

    # Sort by creation time (newest first)
    backups.sort(key=lambda x: x["created"], reverse=True)
    return backups


def cleanup_old_backups():
    """Remove backups older than retention period"""
    ensure_backup_directory()

    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    removed_count = 0

    for file in BACKUP_DIR.glob("*.sql.gz"):
        file_time = datetime.fromtimestamp(file.stat().st_mtime)
        if file_time < cutoff_date:
            logger.info(f"Removing old backup: {file}")
            file.unlink()
            removed_count += 1

    logger.info(f"✅ Cleaned up {removed_count} old backups")


def verify_backup(backup_file: Path) -> bool:
    """Verify backup file integrity"""
    if not backup_file.exists():
        return False

    try:
        # Check if it's a valid gzipped file
        if backup_file.suffix == '.gz':
            result = subprocess.run(["gzip", "-t", str(backup_file)],
                                  capture_output=True)
            return result.returncode == 0
        else:
            # Check if it's a valid SQL file (basic check)
            with open(backup_file, 'r') as f:
                first_line = f.readline()
                return 'PostgreSQL database dump' in first_line
    except Exception:
        return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="BEC CRM Backup/Restore Utility")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create a database backup")
    backup_parser.add_argument("--name", help="Custom backup name")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup", help="Backup file name or path")
    restore_parser.add_argument("--target-db", help="Target database name")

    # List command
    subparsers.add_parser("list", help="List available backups")

    # Cleanup command
    subparsers.add_parser("cleanup", help="Remove old backups")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify backup integrity")
    verify_parser.add_argument("backup", help="Backup file to verify")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "backup":
            backup_file = create_backup(args.name)
            print(f"Backup created: {backup_file}")

        elif args.command == "restore":
            backup_path = Path(args.backup)
            if not backup_path.is_absolute():
                backup_path = BACKUP_DIR / backup_path

            success = restore_backup(backup_path, args.target_db)
            if success:
                print("Backup restored successfully")
            else:
                print("Backup restore failed")
                sys.exit(1)

        elif args.command == "list":
            backups = list_backups()
            if backups:
                print("\nAvailable backups:")
                print("-" * 80)
                for backup in backups:
                    size_mb = backup["size"] / (1024 * 1024)
                    print(f"{backup['name']:<40} {size_mb:>8.1f} MB  {backup['created']}")
            else:
                print("No backups found")

        elif args.command == "cleanup":
            cleanup_old_backups()
            print("Cleanup completed")

        elif args.command == "verify":
            backup_path = Path(args.backup)
            if not backup_path.is_absolute():
                backup_path = BACKUP_DIR / backup_path

            if verify_backup(backup_path):
                print("✅ Backup file is valid")
            else:
                print("❌ Backup file is invalid or corrupted")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()