import pytest
from httpx import AsyncClient


class TestKiosk:
    """Test kiosk check-in functionality"""

    async def test_kiosk_client_lookup_by_phone(self, test_client: AsyncClient, test_client_data):
        """Test looking up client by phone number (no auth required)"""
        phone = test_client_data["phone"]

        response = await test_client.get(f"/api/v1/checkins/lookup?phone={phone}")

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "John Doe"
        assert data["phone"] == phone

    async def test_kiosk_client_lookup_by_code(self, test_client: AsyncClient, test_client_data):
        """Test looking up client by member code (no auth required)"""
        # Use the client ID as a code for testing
        code = test_client_data["id"][:8]  # Use first 8 chars of UUID

        response = await test_client.get(f"/api/v1/checkins/lookup?code={code}")

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "John Doe"

    async def test_kiosk_client_lookup_not_found(self, test_client: AsyncClient):
        """Test lookup with non-existent phone/code"""
        response = await test_client.get("/api/v1/checkins/lookup?phone=9999999999")

        assert response.status_code == 200
        assert response.json() is None

    async def test_kiosk_client_lookup_no_params(self, test_client: AsyncClient):
        """Test lookup without phone or code parameters"""
        response = await test_client.get("/api/v1/checkins/lookup")

        assert response.status_code == 400
        assert "Must provide phone or code" in response.json()["detail"]

    async def test_kiosk_checkin_by_phone(self, test_client: AsyncClient, test_client_data):
        """Test kiosk check-in by phone (no auth required)"""
        checkin_data = {
            "phone": test_client_data["phone"],
            "station": "Kiosk-1"
        }

        response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)

        assert response.status_code == 201
        data = response.json()
        assert data["client_name"] == "John Doe"
        assert data["method"] == "kiosk"
        assert data["station"] == "Kiosk-1"

    async def test_kiosk_checkin_by_code(self, test_client: AsyncClient, test_client_data):
        """Test kiosk check-in by member code (no auth required)"""
        checkin_data = {
            "code": test_client_data["id"][:8],
            "station": "Kiosk-2"
        }

        response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)

        assert response.status_code == 201
        data = response.json()
        assert data["client_name"] == "John Doe"
        assert data["method"] == "kiosk"
        assert data["station"] == "Kiosk-2"

    async def test_kiosk_checkin_client_not_found(self, test_client: AsyncClient):
        """Test kiosk check-in with non-existent client"""
        checkin_data = {
            "phone": "9999999999",
            "station": "Kiosk-1"
        }

        response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)

        assert response.status_code == 404
        assert "Client not found" in response.json()["detail"]

    async def test_kiosk_checkin_no_identifier(self, test_client: AsyncClient):
        """Test kiosk check-in without phone or code"""
        checkin_data = {
            "station": "Kiosk-1"
        }

        response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)

        assert response.status_code == 422  # Validation error

    async def test_staff_checkin(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test staff-assisted check-in"""
        checkin_data = {
            "client_id": test_client_data["id"],
            "method": "staff",
            "station": "Station-A",
            "notes": "Staff assisted check-in"
        }

        response = await test_client.post("/api/v1/checkins",
            headers=staff_auth_headers,
            json=checkin_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["client_name"] == "John Doe"
        assert data["method"] == "staff"
        assert data["station"] == "Station-A"

    async def test_get_recent_checkins(self, test_client: AsyncClient, staff_auth_headers):
        """Test retrieving recent check-ins (staff only)"""
        response = await test_client.get("/api/v1/checkins", headers=staff_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_client_checkins(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test retrieving check-ins for specific client"""
        client_id = test_client_data["id"]

        response = await test_client.get(f"/api/v1/clients/{client_id}/checkins",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_checkin_stats(self, test_client: AsyncClient, staff_auth_headers):
        """Test retrieving check-in statistics"""
        response = await test_client.get("/api/v1/checkins/stats",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "today" in data
        assert "this_week" in data
        assert "this_month" in data
        assert "unique_clients_today" in data
        assert "popular_stations" in data

    async def test_unauthorized_staff_endpoints(self, test_client: AsyncClient):
        """Test that staff endpoints require authentication"""
        # Test accessing staff check-ins endpoint without auth
        response = await test_client.get("/api/v1/checkins")
        assert response.status_code == 403

        # Test creating staff check-in without auth
        response = await test_client.post("/api/v1/checkins", json={
            "client_id": "test-id",
            "method": "staff"
        })
        assert response.status_code == 403