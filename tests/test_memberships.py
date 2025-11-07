import pytest
from httpx import AsyncClient
from datetime import date, timedelta


class TestMemberships:
    """Test membership management functionality"""

    def test_membership_status_calculation(self):
        """Test membership status logic (unit test)"""
        from modules.memberships.models import Membership

        today = date.today()

        # Test active membership
        active_membership = Membership(
            plan_code="unlimited",
            starts_on=today - timedelta(days=10),
            ends_on=today + timedelta(days=20)
        )
        assert active_membership.status == "active"
        assert active_membership.is_active
        assert not active_membership.is_expired

        # Test expired membership
        expired_membership = Membership(
            plan_code="unlimited",
            starts_on=today - timedelta(days=40),
            ends_on=today - timedelta(days=10)
        )
        assert expired_membership.status == "expired"
        assert expired_membership.is_expired
        assert not expired_membership.is_active

        # Test pending membership
        pending_membership = Membership(
            plan_code="unlimited",
            starts_on=today + timedelta(days=5),
            ends_on=today + timedelta(days=35)
        )
        assert pending_membership.status == "pending"
        assert pending_membership.is_pending
        assert not pending_membership.is_active

    def test_days_remaining_calculation(self):
        """Test days remaining calculation"""
        from modules.memberships.models import Membership

        today = date.today()

        # Active membership with 15 days remaining
        membership = Membership(
            plan_code="unlimited",
            starts_on=today - timedelta(days=5),
            ends_on=today + timedelta(days=15)
        )
        assert membership.days_remaining == 15

        # Expired membership
        expired_membership = Membership(
            plan_code="unlimited",
            starts_on=today - timedelta(days=40),
            ends_on=today - timedelta(days=10)
        )
        assert expired_membership.days_remaining == 0

    def test_expiring_soon_logic(self):
        """Test expiring soon detection"""
        from modules.memberships.models import Membership

        today = date.today()

        # Membership expiring in 10 days (within 30-day threshold)
        expiring_membership = Membership(
            plan_code="unlimited",
            starts_on=today - timedelta(days=20),
            ends_on=today + timedelta(days=10)
        )
        assert expiring_membership.is_expiring_soon(30)
        assert expiring_membership.is_expiring_soon(15)
        assert not expiring_membership.is_expiring_soon(5)

    async def test_create_membership(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test creating a membership for a client"""
        client_id = test_client_data["id"]
        membership_data = {
            "plan_code": "unlimited",
            "starts_on": date.today().isoformat(),
            "ends_on": (date.today() + timedelta(days=30)).isoformat(),
            "notes": "Test membership"
        }

        response = await test_client.post(f"/api/v1/clients/{client_id}/membership",
            headers=staff_auth_headers,
            json=membership_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["plan_code"] == "unlimited"
        assert data["client_id"] == client_id
        assert data["status"] == "active"

    async def test_create_membership_invalid_dates(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test creating membership with invalid dates"""
        client_id = test_client_data["id"]
        membership_data = {
            "plan_code": "unlimited",
            "starts_on": date.today().isoformat(),
            "ends_on": (date.today() - timedelta(days=1)).isoformat(),  # End before start
            "notes": "Invalid membership"
        }

        response = await test_client.post(f"/api/v1/clients/{client_id}/membership",
            headers=staff_auth_headers,
            json=membership_data
        )

        assert response.status_code == 422  # Validation error

    async def test_get_client_membership(self, test_client: AsyncClient, staff_auth_headers, test_membership_data):
        """Test retrieving client's current membership"""
        client_id = test_membership_data["client_id"]

        response = await test_client.get(f"/api/v1/clients/{client_id}/membership",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_membership_data["id"]
        assert data["plan_code"] == "unlimited"

    async def test_get_membership_by_id(self, test_client: AsyncClient, staff_auth_headers, test_membership_data):
        """Test retrieving membership by ID"""
        membership_id = test_membership_data["id"]

        response = await test_client.get(f"/api/v1/memberships/{membership_id}",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == membership_id
        assert data["plan_code"] == "unlimited"

    async def test_update_membership(self, test_client: AsyncClient, staff_auth_headers, test_membership_data):
        """Test updating membership"""
        membership_id = test_membership_data["id"]
        update_data = {
            "plan_code": "premium",
            "notes": "Updated to premium"
        }

        response = await test_client.patch(f"/api/v1/memberships/{membership_id}",
            headers=staff_auth_headers,
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["plan_code"] == "premium"
        assert data["notes"] == "Updated to premium"

    async def test_delete_membership(self, test_client: AsyncClient, staff_auth_headers, test_membership_data):
        """Test deleting membership"""
        membership_id = test_membership_data["id"]

        response = await test_client.delete(f"/api/v1/memberships/{membership_id}",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify it's gone
        get_response = await test_client.get(f"/api/v1/memberships/{membership_id}",
            headers=staff_auth_headers
        )
        assert get_response.status_code == 404

    async def test_get_expiring_memberships(self, test_client: AsyncClient, staff_auth_headers):
        """Test retrieving expiring memberships"""
        response = await test_client.get("/api/v1/memberships/expiring?days=30",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_membership_stats(self, test_client: AsyncClient, staff_auth_headers, test_session, test_membership_data):
        """Test retrieving membership statistics"""
        from modules.core_clients.models import Client
        from modules.memberships.models import Membership

        today = date.today()

        # Create an expired membership to ensure the expired branch is exercised
        expired_client = Client(
            first_name="Expired",
            last_name="Member",
            email="expired.member@example.com",
            phone="5550001111",
            external_ids={"member_code": "EXPIRED001"}
        )
        test_session.add(expired_client)
        await test_session.commit()
        await test_session.refresh(expired_client)

        expired_membership = Membership(
            client_id=expired_client.id,
            plan_code="limited",
            starts_on=today - timedelta(days=60),
            ends_on=today - timedelta(days=10),
            notes="Expired membership"
        )
        test_session.add(expired_membership)
        await test_session.commit()

        response = await test_client.get(
            "/api/v1/memberships/stats",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert set(data.keys()) == {"total_active", "expiring_30_days", "expired", "plans"}
        # test_membership_data fixture creates one active membership expiring in 30 days
        assert data["total_active"] == 1
        assert data["expiring_30_days"] == 1
        assert data["expired"] == 1
        assert data["plans"] == {"unlimited": 1}
