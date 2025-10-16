import pytest
from datetime import datetime

from auth_workaround import User, create_access_token, pwd_context


@pytest.mark.asyncio
async def test_update_username_preserves_email(test_client, test_session):
    """Ensure updating username does not change stored email."""
    now = datetime.utcnow()

    admin_user = User(
        username="adminuser",
        email="admin@example.com",
        password_hash=pwd_context.hash("AdminPass123!"),
        role="admin",
        is_active=True,
        dark_mode=False,
        created_at=now,
        updated_at=now,
    )

    member_user = User(
        username="memberuser",
        email="member@example.com",
        password_hash=pwd_context.hash("MemberPass123!"),
        role="staff",
        is_active=True,
        dark_mode=False,
        created_at=now,
        updated_at=now,
    )

    test_session.add_all([admin_user, member_user])
    await test_session.commit()
    await test_session.refresh(admin_user)
    await test_session.refresh(member_user)

    token = create_access_token(
        data={
            "sub": str(admin_user.id),
            "username": admin_user.username,
            "email": admin_user.email,
            "role": admin_user.role,
        }
    )

    response = await test_client.patch(
        f"/api/v1/users/{member_user.id}",
        json={"username": "updatedmember"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updatedmember"
    assert data["email"] == "member@example.com"

    await test_session.refresh(member_user)
    assert member_user.email == "member@example.com"
