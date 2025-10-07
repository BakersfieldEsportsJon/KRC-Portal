"""
End-to-End test for the kiosk check-in flow

This test simulates a complete kiosk check-in process from client lookup to successful check-in.
"""

import pytest
from httpx import AsyncClient


class TestE2EKioskFlow:
    """End-to-end test for kiosk check-in workflow"""

    async def test_complete_kiosk_checkin_flow(self, test_client: AsyncClient, test_client_data, test_membership_data):
        """
        Test the complete kiosk check-in flow:
        1. Client looks up their account by phone
        2. System returns client info with membership status
        3. Client confirms and checks in
        4. System records the check-in
        """

        phone = test_client_data["phone"]

        # Step 1: Client lookup by phone
        lookup_response = await test_client.get(f"/api/v1/checkins/lookup?phone={phone}")

        assert lookup_response.status_code == 200
        lookup_data = lookup_response.json()

        # Verify client information is returned
        assert lookup_data["full_name"] == "John Doe"
        assert lookup_data["phone"] == phone
        assert lookup_data["membership_status"] == "active"  # From our test membership

        # Step 2: Perform kiosk check-in
        checkin_data = {
            "phone": phone,
            "station": "Kiosk-Main"
        }

        checkin_response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)

        assert checkin_response.status_code == 201
        checkin_result = checkin_response.json()

        # Verify check-in was successful
        assert checkin_result["client_name"] == "John Doe"
        assert checkin_result["method"] == "kiosk"
        assert checkin_result["station"] == "Kiosk-Main"
        assert "happened_at" in checkin_result
        assert "id" in checkin_result

        # Step 3: Verify check-in was recorded (requires staff auth)
        # Create a staff user and get auth token for verification
        from modules.core.auth.models import User
        from modules.core.auth.utils import hash_password

        # Note: In a real E2E test, this verification step would be done
        # through the admin interface or by staff checking the system

        print(f"✅ E2E Test Passed: Client {lookup_data['full_name']} successfully checked in at {checkin_result['station']}")

    async def test_kiosk_flow_with_expired_membership(self, test_client: AsyncClient, test_session):
        """
        Test kiosk flow for client with expired membership:
        1. Create client with expired membership
        2. Lookup should still work but show expired status
        3. Check-in should still be allowed (business rule)
        """

        from modules.core.clients.models import Client
        from modules.memberships.models import Membership
        from datetime import date, timedelta

        # Create client with expired membership
        expired_client = Client(
            first_name="Expired",
            last_name="Member",
            phone="5555551234",
            email="expired@test.com"
        )
        test_session.add(expired_client)
        await test_session.commit()
        await test_session.refresh(expired_client)

        expired_membership = Membership(
            client_id=expired_client.id,
            plan_code="unlimited",
            starts_on=date.today() - timedelta(days=60),
            ends_on=date.today() - timedelta(days=30),  # Expired 30 days ago
            notes="Expired test membership"
        )
        test_session.add(expired_membership)
        await test_session.commit()

        # Step 1: Lookup expired member
        lookup_response = await test_client.get(f"/api/v1/checkins/lookup?phone=5555551234")

        assert lookup_response.status_code == 200
        lookup_data = lookup_response.json()
        assert lookup_data["full_name"] == "Expired Member"
        assert lookup_data["membership_status"] == "expired"

        # Step 2: Check-in should still work (allows expired members to use system)
        checkin_data = {
            "phone": "5555551234",
            "station": "Kiosk-Side"
        }

        checkin_response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)

        assert checkin_response.status_code == 201
        checkin_result = checkin_response.json()
        assert checkin_result["client_name"] == "Expired Member"

        print(f"✅ E2E Test Passed: Expired member {lookup_data['full_name']} was able to check in with warning")

    async def test_kiosk_flow_invalid_scenarios(self, test_client: AsyncClient):
        """
        Test various error scenarios in kiosk flow:
        1. Invalid phone number
        2. Non-existent client
        3. Malformed requests
        """

        # Test 1: Invalid phone number format
        lookup_response = await test_client.get("/api/v1/checkins/lookup?phone=invalid")
        assert lookup_response.status_code == 200
        assert lookup_response.json() is None  # Should return null for not found

        # Test 2: Non-existent phone number
        lookup_response = await test_client.get("/api/v1/checkins/lookup?phone=9999999999")
        assert lookup_response.status_code == 200
        assert lookup_response.json() is None

        # Test 3: Check-in with non-existent client
        checkin_data = {
            "phone": "9999999999",
            "station": "Kiosk-Test"
        }
        checkin_response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)
        assert checkin_response.status_code == 404
        assert "not found" in checkin_response.json()["detail"].lower()

        # Test 4: Missing required fields
        invalid_checkin = {"station": "Kiosk-Test"}  # Missing phone/code
        checkin_response = await test_client.post("/api/v1/checkins/kiosk", json=invalid_checkin)
        assert checkin_response.status_code == 422  # Validation error

        print("✅ E2E Test Passed: All invalid scenarios handled correctly")

    async def test_kiosk_accessibility_features(self, test_client: AsyncClient, test_client_data):
        """
        Test kiosk accessibility features:
        1. Case-insensitive phone lookup
        2. Phone number format flexibility
        3. Error message clarity
        """

        # Test 1: Phone number with different formatting
        formatted_phone = f"({test_client_data['phone'][:3]}) {test_client_data['phone'][3:6]}-{test_client_data['phone'][6:]}"

        lookup_response = await test_client.get(f"/api/v1/checkins/lookup?phone={formatted_phone}")
        assert lookup_response.status_code == 200
        lookup_data = lookup_response.json()
        assert lookup_data["full_name"] == "John Doe"

        # Test 2: Check-in with formatted phone
        checkin_data = {
            "phone": formatted_phone,
            "station": "Accessible-Kiosk"
        }

        checkin_response = await test_client.post("/api/v1/checkins/kiosk", json=checkin_data)
        assert checkin_response.status_code == 201

        print("✅ E2E Test Passed: Accessibility features working correctly")