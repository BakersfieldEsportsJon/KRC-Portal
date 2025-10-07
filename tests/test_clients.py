import pytest
from httpx import AsyncClient


class TestClients:
    """Test client management endpoints"""

    async def test_create_client(self, test_client: AsyncClient, staff_auth_headers):
        """Test creating a new client"""
        client_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "5559876543",
            "external_ids": {"member_code": "TEST002"}
        }

        response = await test_client.post("/api/v1/clients",
            headers=staff_auth_headers,
            json=client_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["email"] == "jane.smith@example.com"
        assert "id" in data

    async def test_create_client_invalid_data(self, test_client: AsyncClient, staff_auth_headers):
        """Test creating client with invalid data"""
        client_data = {
            "first_name": "",  # Invalid - empty name
            "last_name": "Smith",
            "email": "invalid-email",  # Invalid email format
            "phone": "123"  # Invalid phone
        }

        response = await test_client.post("/api/v1/clients",
            headers=staff_auth_headers,
            json=client_data
        )

        assert response.status_code == 422  # Validation error

    async def test_get_clients(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test retrieving clients list"""
        response = await test_client.get("/api/v1/clients", headers=staff_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least our test client

    async def test_search_clients(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test searching clients"""
        response = await test_client.get("/api/v1/clients?query=John",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find our test client "John Doe"
        assert any(client["first_name"] == "John" for client in data)

    async def test_get_client_by_id(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test retrieving specific client"""
        client_id = test_client_data["id"]
        response = await test_client.get(f"/api/v1/clients/{client_id}",
            headers=staff_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == client_id
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    async def test_get_nonexistent_client(self, test_client: AsyncClient, staff_auth_headers):
        """Test retrieving non-existent client"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.get(f"/api/v1/clients/{fake_id}",
            headers=staff_auth_headers
        )

        assert response.status_code == 404

    async def test_update_client(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test updating client information"""
        client_id = test_client_data["id"]
        update_data = {
            "first_name": "Johnny",
            "phone": "5551111111"
        }

        response = await test_client.patch(f"/api/v1/clients/{client_id}",
            headers=staff_auth_headers,
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Johnny"
        assert data["phone"] == "5551111111"
        assert data["last_name"] == "Doe"  # Unchanged

    async def test_delete_client(self, test_client: AsyncClient, staff_auth_headers):
        """Test deleting a client"""
        # First create a client to delete
        client_data = {
            "first_name": "Delete",
            "last_name": "Me",
            "email": "delete@example.com"
        }

        create_response = await test_client.post("/api/v1/clients",
            headers=staff_auth_headers,
            json=client_data
        )
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]

        # Now delete it
        delete_response = await test_client.delete(f"/api/v1/clients/{client_id}",
            headers=staff_auth_headers
        )

        assert delete_response.status_code == 200
        assert "deleted successfully" in delete_response.json()["message"]

        # Verify it's gone
        get_response = await test_client.get(f"/api/v1/clients/{client_id}",
            headers=staff_auth_headers
        )
        assert get_response.status_code == 404

    async def test_add_tags_to_client(self, test_client: AsyncClient, staff_auth_headers, test_client_data):
        """Test adding tags to client"""
        client_id = test_client_data["id"]
        tags_data = {
            "tag_names": ["VIP", "Regular"]
        }

        response = await test_client.post(f"/api/v1/clients/{client_id}/tags",
            headers=staff_auth_headers,
            json=tags_data
        )

        assert response.status_code == 200
        data = response.json()
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "VIP" in tag_names
        assert "Regular" in tag_names

    async def test_get_all_tags(self, test_client: AsyncClient, staff_auth_headers):
        """Test retrieving all available tags"""
        response = await test_client.get("/api/v1/tags", headers=staff_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_unauthorized_access(self, test_client: AsyncClient):
        """Test that endpoints require authentication"""
        response = await test_client.get("/api/v1/clients")
        assert response.status_code == 403  # No auth header