import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add apps to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from apps.api.main import app
from apps.api.core.database import Base, get_db
from modules.core.auth.models import User
from modules.core.auth.utils import hash_password

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def test_client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database dependency override"""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sync_test_client() -> Generator[TestClient, None, None]:
    """Create synchronous test client for simple tests"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def test_admin_user(test_session) -> User:
    """Create test admin user"""
    user = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def test_staff_user(test_session) -> User:
    """Create test staff user"""
    user = User(
        email="staff@test.com",
        password_hash=hash_password("staff123"),
        role="staff",
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def admin_auth_headers(test_client, test_admin_user) -> dict:
    """Get authentication headers for admin user"""
    response = await test_client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    token_data = response.json()

    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
async def staff_auth_headers(test_client, test_staff_user) -> dict:
    """Get authentication headers for staff user"""
    response = await test_client.post("/api/v1/auth/login", json={
        "email": "staff@test.com",
        "password": "staff123"
    })
    assert response.status_code == 200
    token_data = response.json()

    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
async def test_client_data(test_session) -> dict:
    """Create test client data"""
    from modules.core.clients.models import Client

    client = Client(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="5551234567",
        external_ids={"member_code": "TEST001"}
    )
    test_session.add(client)
    await test_session.commit()
    await test_session.refresh(client)

    return {
        "id": str(client.id),
        "first_name": client.first_name,
        "last_name": client.last_name,
        "email": client.email,
        "phone": client.phone
    }


@pytest.fixture
async def test_membership_data(test_session, test_client_data) -> dict:
    """Create test membership data"""
    from modules.memberships.models import Membership
    from datetime import date, timedelta

    membership = Membership(
        client_id=test_client_data["id"],
        plan_code="unlimited",
        starts_on=date.today(),
        ends_on=date.today() + timedelta(days=30),
        notes="Test membership"
    )
    test_session.add(membership)
    await test_session.commit()
    await test_session.refresh(membership)

    return {
        "id": str(membership.id),
        "client_id": str(membership.client_id),
        "plan_code": membership.plan_code,
        "starts_on": membership.starts_on.isoformat(),
        "ends_on": membership.ends_on.isoformat()
    }