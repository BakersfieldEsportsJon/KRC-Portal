#!/usr/bin/env python3
"""
Seed script for BEC CRM system

Creates demo data including:
- 20 demo clients with various membership statuses
- Sample memberships across different plans
- Check-in history
- Tags and consents
- Admin and staff users
"""

import sys
import os
import asyncio
from datetime import date, datetime, timedelta
import random
from faker import Faker

# Add apps to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from modules.core.auth.models import User
from modules.core.auth.utils import hash_password
from modules.core.clients.models import Client, Tag, ContactMethod, Consent
from modules.memberships.models import Membership
from modules.kiosk.models import CheckIn, CheckInMethod
from modules.ggleap.models import GgleapGroup, GgleapGroupType
from apps.api.core.config import settings

fake = Faker()

# Demo membership plans
MEMBERSHIP_PLANS = [
    "unlimited",
    "10_hours",
    "20_hours",
    "day_pass",
    "student",
    "tournament"
]

# Demo tags
DEMO_TAGS = [
    {"name": "VIP", "description": "VIP member", "color": "#FFD700"},
    {"name": "Student", "description": "Student discount", "color": "#4CAF50"},
    {"name": "Tournament", "description": "Tournament player", "color": "#FF5722"},
    {"name": "Regular", "description": "Regular member", "color": "#2196F3"},
    {"name": "New", "description": "New member", "color": "#9C27B0"},
    {"name": "Inactive", "description": "Inactive member", "color": "#757575"}
]

# Gaming stations
GAMING_STATIONS = [
    "Station-001", "Station-002", "Station-003", "Station-004", "Station-005",
    "Station-006", "Station-007", "Station-008", "Station-009", "Station-010",
    "VIP-Station-A", "VIP-Station-B", "Tournament-PC-1", "Tournament-PC-2",
    "Console-Area-1", "Console-Area-2", "Kiosk-Main", "Kiosk-Side"
]


async def create_engine():
    """Create database engine"""
    return create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False
    )


async def create_admin_users(session: AsyncSession):
    """Create admin and staff users"""
    print("Creating admin and staff users...")

    # Admin user
    admin = User(
        email="admin@bakersfieldesports.com",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )
    session.add(admin)

    # Staff users
    staff_users = [
        {
            "email": "manager@bakersfieldesports.com",
            "password": "manager123",
            "role": "staff"
        },
        {
            "email": "staff1@bakersfieldesports.com",
            "password": "staff123",
            "role": "staff"
        },
        {
            "email": "staff2@bakersfieldesports.com",
            "password": "staff123",
            "role": "staff"
        }
    ]

    for user_data in staff_users:
        user = User(
            email=user_data["email"],
            password_hash=hash_password(user_data["password"]),
            role=user_data["role"],
            is_active=True
        )
        session.add(user)

    await session.commit()
    print("✓ Created admin and staff users")


async def create_tags(session: AsyncSession):
    """Create demo tags"""
    print("Creating tags...")

    for tag_data in DEMO_TAGS:
        tag = Tag(
            name=tag_data["name"],
            description=tag_data["description"],
            color=tag_data["color"]
        )
        session.add(tag)

    await session.commit()
    print("✓ Created tags")


async def create_ggleap_groups(session: AsyncSession):
    """Create ggLeap group mappings"""
    print("Creating ggLeap group mappings...")

    # Active members group
    active_group = GgleapGroup(
        map_key=GgleapGroupType.ACTIVE,
        ggleap_group_id="group_active_123",
        group_name="KRC Unlimited"
    )
    session.add(active_group)

    # Expired members group
    expired_group = GgleapGroup(
        map_key=GgleapGroupType.EXPIRED,
        ggleap_group_id="group_expired_456",
        group_name="Kern Regional Center"
    )
    session.add(expired_group)

    await session.commit()
    print("✓ Created ggLeap group mappings")


async def create_demo_clients(session: AsyncSession):
    """Create 20 demo clients with various data"""
    print("Creating demo clients...")

    # Get tags for random assignment
    tags = await session.execute("SELECT id, name FROM tags")
    tag_list = tags.fetchall()

    clients = []

    for i in range(20):
        # Generate realistic client data
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
        phone = fake.phone_number()[:10]  # Ensure 10 digits

        # Clean phone number to digits only
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) != 10:
            phone = f"555{fake.random_int(1000000, 9999999)}"

        client = Client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            date_of_birth=fake.date_of_birth(minimum_age=16, maximum_age=65),
            external_ids={
                "member_code": f"BEC{1000 + i:04d}",
                "legacy_id": fake.random_int(10000, 99999)
            }
        )
        session.add(client)
        clients.append(client)

        # Add some contact methods
        if random.choice([True, False]):
            contact_method = ContactMethod(
                client=client,
                type=random.choice(["sms", "email", "discord"]),
                value=email if random.choice([True, False]) else phone,
                verified=random.choice([True, False])
            )
            session.add(contact_method)

        # Add some consents
        for consent_type in ["sms", "email", "photo", "tos", "waiver"]:
            if random.choice([True, False, False]):  # 33% chance
                consent = Consent(
                    client=client,
                    kind=consent_type,
                    granted=random.choice([True, False]),
                    granted_at=fake.date_time_this_year() if random.choice([True, False]) else None,
                    source=random.choice(["website", "kiosk", "staff", "phone"])
                )
                session.add(consent)

    await session.commit()

    # Add tags to clients (after commit to get IDs)
    for i, client in enumerate(clients):
        await session.refresh(client)

        # Randomly assign 1-3 tags to each client
        num_tags = random.randint(1, 3)
        selected_tags = random.sample(tag_list, min(num_tags, len(tag_list)))

        for tag_id, tag_name in selected_tags:
            # We need to fetch the actual tag objects
            tag_result = await session.execute(f"SELECT * FROM tags WHERE id = '{tag_id}'")
            if tag_result.fetchone():
                await session.execute(
                    f"INSERT INTO client_tags (client_id, tag_id) VALUES ('{client.id}', '{tag_id}')"
                )

    await session.commit()
    print("✓ Created 20 demo clients with tags and consents")
    return clients


async def create_demo_memberships(session: AsyncSession, clients: list):
    """Create memberships for clients with various statuses"""
    print("Creating demo memberships...")

    today = date.today()

    for i, client in enumerate(clients):
        # 80% of clients have memberships
        if random.random() < 0.8:
            plan = random.choice(MEMBERSHIP_PLANS)

            # Create different membership scenarios
            scenario = random.choice(["active", "expired", "expiring_soon", "future"])

            if scenario == "active":
                # Active membership
                starts_on = today - timedelta(days=random.randint(1, 180))
                ends_on = today + timedelta(days=random.randint(1, 180))
            elif scenario == "expired":
                # Expired membership
                starts_on = today - timedelta(days=random.randint(60, 365))
                ends_on = today - timedelta(days=random.randint(1, 60))
            elif scenario == "expiring_soon":
                # Expiring within 30 days
                starts_on = today - timedelta(days=random.randint(30, 180))
                ends_on = today + timedelta(days=random.randint(1, 30))
            else:  # future
                # Future membership
                starts_on = today + timedelta(days=random.randint(1, 30))
                ends_on = starts_on + timedelta(days=random.randint(30, 365))

            membership = Membership(
                client_id=client.id,
                plan_code=plan,
                starts_on=starts_on,
                ends_on=ends_on,
                notes=f"Demo membership for {client.first_name} {client.last_name}"
            )
            session.add(membership)

    await session.commit()
    print("✓ Created demo memberships with various statuses")


async def create_demo_checkins(session: AsyncSession, clients: list):
    """Create check-in history for clients"""
    print("Creating demo check-ins...")

    # Create check-ins for the past 30 days
    start_date = datetime.now() - timedelta(days=30)

    for day in range(30):
        check_date = start_date + timedelta(days=day)

        # Random number of check-ins per day (0-15)
        daily_checkins = random.randint(0, 15)

        for _ in range(daily_checkins):
            client = random.choice(clients)
            method = random.choice([CheckInMethod.KIOSK, CheckInMethod.STAFF])
            station = random.choice(GAMING_STATIONS)

            # Random time during business hours (10 AM to 11 PM)
            hour = random.randint(10, 23)
            minute = random.randint(0, 59)
            happened_at = check_date.replace(hour=hour, minute=minute)

            checkin = CheckIn(
                client_id=client.id,
                method=method,
                station=station,
                happened_at=happened_at,
                notes=f"Demo check-in via {method.value}"
            )
            session.add(checkin)

    await session.commit()
    print("✓ Created demo check-in history for the past 30 days")


async def main():
    """Main seed function"""
    print("🌱 Starting BEC CRM seed data creation...")

    # Create database engine
    engine = await create_engine()

    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Create all seed data
            await create_admin_users(session)
            await create_tags(session)
            await create_ggleap_groups(session)

            clients = await create_demo_clients(session)
            await create_demo_memberships(session, clients)
            await create_demo_checkins(session, clients)

            print("\n🎉 Seed data creation completed successfully!")
            print("\n📋 Summary:")
            print("   • Admin user: admin@bakersfieldesports.com (password: admin123)")
            print("   • Staff users: manager@bakersfieldesports.com, staff1@bakersfieldesports.com, staff2@bakersfieldesports.com")
            print("   • 20 demo clients with various membership statuses")
            print("   • Demo tags, consents, and contact methods")
            print("   • 30 days of check-in history")
            print("   • ggLeap group mappings")
            print("\n🚀 You can now start the application and explore the demo data!")

        except Exception as e:
            print(f"❌ Error creating seed data: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())