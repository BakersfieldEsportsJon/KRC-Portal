#!/usr/bin/env python3
"""
Production User Setup Script
This script helps you:
1. Create a new admin account for production
2. Disable or delete demo accounts
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from passlib.context import CryptContext
import asyncio
from sqlalchemy import select, delete
from uuid import uuid4
from datetime import datetime

# Import from apps/api
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))
from models import User
from core.database import AsyncSessionLocal


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


async def create_admin_user(email: str, password: str):
    """Create a new admin user"""
    async with AsyncSessionLocal() as db:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()

        if existing:
            print(f"❌ User {email} already exists!")
            return False

        # Create new admin user
        admin = User(
            id=uuid4(),
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(admin)
        await db.commit()
        print(f"✅ Created admin user: {email}")
        return True


async def disable_demo_accounts():
    """Disable demo accounts"""
    demo_emails = [
        "admin@bakersfieldesports.com",
        "staff1@bakersfieldesports.com",
        "staff@bakersfieldesports.com"
    ]

    async with AsyncSessionLocal() as db:
        for email in demo_emails:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if user:
                user.is_active = False
                print(f"🔒 Disabled demo account: {email}")

        await db.commit()

    print("✅ All demo accounts disabled")


async def delete_demo_accounts():
    """Delete demo accounts (use with caution!)"""
    demo_emails = [
        "admin@bakersfieldesports.com",
        "staff1@bakersfieldesports.com",
        "staff@bakersfieldesports.com"
    ]

    async with AsyncSessionLocal() as db:
        for email in demo_emails:
            await db.execute(delete(User).where(User.email == email))
            print(f"🗑️  Deleted demo account: {email}")

        await db.commit()

    print("✅ All demo accounts deleted")


async def list_users():
    """List all users"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

        print("\n📋 Current Users:")
        print("-" * 70)
        for user in users:
            status = "✓ Active" if user.is_active else "✗ Disabled"
            print(f"  {user.email:<40} | {user.role:<10} | {status}")
        print("-" * 70)
        print(f"Total: {len(users)} users\n")


async def main():
    print("=" * 70)
    print("Production User Setup")
    print("=" * 70)
    print()
    print("Choose an option:")
    print("  1. Create new admin account")
    print("  2. Disable demo accounts")
    print("  3. Delete demo accounts (PERMANENT)")
    print("  4. List all users")
    print("  5. Exit")
    print()

    choice = input("Enter choice (1-5): ").strip()

    if choice == "1":
        print("\nCreate New Admin Account")
        print("-" * 70)
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        password_confirm = input("Confirm password: ").strip()

        if password != password_confirm:
            print("❌ Passwords don't match!")
            return

        if len(password) < 8:
            print("❌ Password must be at least 8 characters!")
            return

        await create_admin_user(email, password)

    elif choice == "2":
        print("\nDisable Demo Accounts")
        print("-" * 70)
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            await disable_demo_accounts()
        else:
            print("❌ Cancelled")

    elif choice == "3":
        print("\n⚠️  WARNING: Delete Demo Accounts (PERMANENT)")
        print("-" * 70)
        print("This will permanently delete all demo accounts!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        if confirm == "DELETE":
            await delete_demo_accounts()
        else:
            print("❌ Cancelled")

    elif choice == "4":
        await list_users()

    elif choice == "5":
        print("Goodbye!")
        return

    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
