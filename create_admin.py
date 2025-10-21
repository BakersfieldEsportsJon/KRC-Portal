"""Create admin user in the database"""
import asyncio
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models import User
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.email == "admin@bec.com"))
        user_exists = result.scalar_one_or_none()

        if not user_exists:
            user = User(
                username="admin",
                email="admin@bec.com",
                password_hash=pwd_context.hash("admin123"),
                role="admin",
                is_active=True,
                dark_mode=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(user)
            await session.commit()
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Email: admin@bec.com")
            print("   Password: admin123")
        else:
            print("ℹ️  Admin user already exists")

if __name__ == "__main__":
    asyncio.run(create_admin())
