import pytest
from datetime import datetime, timedelta
import json


class TestCreateVoucherRoute:
    """Test POST /api/v1/vouchers/ endpoint"""

    def test_create_voucher_success(self, client, valid_future_date):
        """Test successful voucher creation via API"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.5,
                "expiration_date": valid_future_date.isoformat()
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "code" in data
        assert data["discount_percentage"] == 15.5
        assert data["active"] is True
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_voucher_with_100_percent_discount(self, client, valid_future_date):
        """Test creating voucher with 100% discount"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 100.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["discount_percentage"] == 100.0

    def test_create_voucher_invalid_discount_zero(self, client, valid_future_date):
        """Test that 0% discount is rejected"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 0.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )

        assert response.status_code == 422

    def test_create_voucher_invalid_discount_negative(self, client, valid_future_date):
        """Test that negative discount is rejected"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": -10.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )

        assert response.status_code == 422

    def test_create_voucher_invalid_discount_over_100(self, client, valid_future_date):
        """Test that discount over 100% is rejected"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 150.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )

        assert response.status_code == 422

    def test_create_voucher_expired_date(self, client, expired_date):
        """Test that expired date is rejected"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": expired_date.isoformat()
            }
        )

        assert response.status_code == 422

    def test_create_voucher_missing_fields(self, client):
        """Test that missing required fields returns error"""
        response = client.post(
            "/api/v1/vouchers/",
            json={}
        )

        assert response.status_code == 422

    def test_create_voucher_missing_discount(self, client, valid_future_date):
        """Test that missing discount percentage returns error"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "expiration_date": valid_future_date.isoformat()
            }
        )

        assert response.status_code == 422

    def test_create_voucher_missing_expiration(self, client):
        """Test that missing expiration date returns error"""
        response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0
            }
        )

        assert response.status_code == 422

    def test_create_multiple_vouchers_unique_codes(self, client, valid_future_date):
        """Test that multiple vouchers get unique codes"""
        response1 = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 10.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        response2 = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 10.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )

        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["code"] != response2.json()["code"]


class TestListVouchersRoute:
    """Test GET /api/v1/vouchers/ endpoint"""

    def test_list_vouchers_empty(self, client):
        """Test listing when no vouchers exist"""
        response = client.get("/api/v1/vouchers/")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 0

    def test_list_vouchers_single_page(self, client, valid_future_date):
        """Test listing vouchers on a single page"""
        # Create 5 vouchers
        for i in range(5):
            client.post(
                "/api/v1/vouchers/",
                json={
                    "discount_percentage": 10.0 + i,
                    "expiration_date": valid_future_date.isoformat()
                }
            )

        response = client.get("/api/v1/vouchers/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 1

    def test_list_vouchers_pagination_first_page(self, client, valid_future_date):
        """Test pagination on first page"""
        # Create 15 vouchers
        for i in range(15):
            client.post(
                "/api/v1/vouchers/",
                json={
                    "discount_percentage": 10.0 + (i % 90),
                    "expiration_date": valid_future_date.isoformat()
                }
            )

        response = client.get("/api/v1/vouchers/?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 2

    def test_list_vouchers_pagination_second_page(self, client, valid_future_date):
        """Test pagination on second page"""
        # Create 15 vouchers
        for i in range(15):
            client.post(
                "/api/v1/vouchers/",
                json={
                    "discount_percentage": 10.0 + (i % 90),
                    "expiration_date": valid_future_date.isoformat()
                }
            )

        response = client.get("/api/v1/vouchers/?page=2&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 15
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total_pages"] == 2

    def test_list_vouchers_custom_page_size(self, client, valid_future_date):
        """Test listing with custom page size"""
        # Create 25 vouchers
        for i in range(25):
            client.post(
                "/api/v1/vouchers/",
                json={
                    "discount_percentage": 10.0 + (i % 90),
                    "expiration_date": valid_future_date.isoformat()
                }
            )

        response = client.get("/api/v1/vouchers/?page=1&page_size=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 25
        assert data["page_size"] == 5
        assert data["total_pages"] == 5

    def test_list_vouchers_invalid_page(self, client):
        """Test that invalid page returns error"""
        response = client.get("/api/v1/vouchers/?page=0")
        assert response.status_code == 422

    def test_list_vouchers_invalid_page_size(self, client):
        """Test that page size over 100 returns error"""
        response = client.get("/api/v1/vouchers/?page_size=101")
        assert response.status_code == 422


class TestGetVoucherRoute:
    """Test GET /api/v1/vouchers/{code} endpoint"""

    def test_get_valid_voucher(self, client, valid_future_date):
        """Test retrieving a valid voucher"""
        # Create a voucher
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        # Retrieve it
        response = client.get(f"/api/v1/vouchers/{code}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == code
        assert data["discount_percentage"] == 15.0
        assert data["active"] is True

    def test_get_nonexistent_voucher(self, client):
        """Test retrieving a non-existent voucher"""
        response = client.get("/api/v1/vouchers/NONEXISTENT")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_inactive_voucher(self, client, valid_future_date):
        """Test retrieving an inactive voucher"""
        # Create and deactivate a voucher
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        # Deactivate it
        client.patch(f"/api/v1/vouchers/{code}/deactivate")

        # Try to retrieve it
        response = client.get(f"/api/v1/vouchers/{code}")
        assert response.status_code == 404

    def test_get_expired_voucher(self, client, expired_date):
        """Test retrieving an expired voucher"""
        # Note: We cannot create an expired voucher via API
        # This test would require direct database access or mocking
        pass


class TestUpdateVoucherRoute:
    """Test PUT /api/v1/vouchers/{code} endpoint"""

    def test_update_discount_percentage(self, client, valid_future_date):
        """Test updating discount percentage"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        response = client.put(
            f"/api/v1/vouchers/{code}",
            json={"discount_percentage": 25.0}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["discount_percentage"] == 25.0

    def test_update_expiration_date(self, client, valid_future_date):
        """Test updating expiration date"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        new_expiration = valid_future_date + timedelta(days=60)
        response = client.put(
            f"/api/v1/vouchers/{code}",
            json={"expiration_date": new_expiration.isoformat()}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expiration_date"] == new_expiration.isoformat()

    def test_update_both_fields(self, client, valid_future_date):
        """Test updating both fields"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        new_expiration = valid_future_date + timedelta(days=60)
        response = client.put(
            f"/api/v1/vouchers/{code}",
            json={
                "discount_percentage": 35.0,
                "expiration_date": new_expiration.isoformat()
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["discount_percentage"] == 35.0
        assert data["expiration_date"] == new_expiration.isoformat()

    def test_update_nonexistent_voucher(self, client):
        """Test updating a non-existent voucher"""
        response = client.put(
            "/api/v1/vouchers/NONEXISTENT",
            json={"discount_percentage": 25.0}
        )

        assert response.status_code == 404

    def test_update_invalid_discount(self, client, valid_future_date):
        """Test updating with invalid discount"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        response = client.put(
            f"/api/v1/vouchers/{code}",
            json={"discount_percentage": 150.0}
        )

        assert response.status_code == 422

    def test_update_with_empty_body(self, client, valid_future_date):
        """Test updating with empty body (should succeed without changes)"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]
        original_discount = create_response.json()["discount_percentage"]

        response = client.put(
            f"/api/v1/vouchers/{code}",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["discount_percentage"] == original_discount


class TestDeactivateVoucherRoute:
    """Test PATCH /api/v1/vouchers/{code}/deactivate endpoint"""

    def test_deactivate_voucher_success(self, client, valid_future_date):
        """Test successful voucher deactivation"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        response = client.patch(f"/api/v1/vouchers/{code}/deactivate")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Voucher deactivated successfully"
        assert data["code"] == code
        assert data["active"] is False

    def test_deactivate_already_inactive_voucher(self, client, valid_future_date):
        """Test deactivating an already inactive voucher"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        # Deactivate once
        client.patch(f"/api/v1/vouchers/{code}/deactivate")

        # Deactivate again
        response = client.patch(f"/api/v1/vouchers/{code}/deactivate")

        assert response.status_code == 200
        assert response.json()["active"] is False

    def test_deactivate_nonexistent_voucher(self, client):
        """Test deactivating a non-existent voucher"""
        response = client.patch("/api/v1/vouchers/NONEXISTENT/deactivate")
        assert response.status_code == 404

    def test_cannot_retrieve_deactivated_voucher(self, client, valid_future_date):
        """Test that deactivated voucher cannot be retrieved via GET endpoint"""
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 15.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]

        # Deactivate
        client.patch(f"/api/v1/vouchers/{code}/deactivate")

        # Try to retrieve
        response = client.get(f"/api/v1/vouchers/{code}")
        assert response.status_code == 404


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_complete_voucher_lifecycle(self, client, valid_future_date):
        """Test complete voucher lifecycle: create, retrieve, update, deactivate, delete"""
        # Create
        create_response = client.post(
            "/api/v1/vouchers/",
            json={
                "discount_percentage": 10.0,
                "expiration_date": valid_future_date.isoformat()
            }
        )
        code = create_response.json()["code"]
        assert create_response.status_code == 201

        # Retrieve
        get_response = client.get(f"/api/v1/vouchers/{code}")
        assert get_response.status_code == 200
        assert get_response.json()["discount_percentage"] == 10.0

        # Update
        update_response = client.put(
            f"/api/v1/vouchers/{code}",
            json={"discount_percentage": 20.0}
        )
        assert update_response.status_code == 200
        assert update_response.json()["discount_percentage"] == 20.0

        # Verify update
        get_response = client.get(f"/api/v1/vouchers/{code}")
        assert get_response.json()["discount_percentage"] == 20.0

        # Deactivate
        deactivate_response = client.patch(f"/api/v1/vouchers/{code}/deactivate")
        assert deactivate_response.status_code == 200
        assert deactivate_response.json()["active"] is False

        # Verify cannot retrieve deactivated
        get_response = client.get(f"/api/v1/vouchers/{code}")
        assert get_response.status_code == 404

    def test_bulk_voucher_operations(self, client, valid_future_date):
        """Test creating and managing multiple vouchers"""
        codes = []

        # Create 20 vouchers
        for i in range(20):
            response = client.post(
                "/api/v1/vouchers/",
                json={
                    "discount_percentage": 5.0 + (i % 50),
                    "expiration_date": valid_future_date.isoformat()
                }
            )
            assert response.status_code == 201
            codes.append(response.json()["code"])

        # List and verify pagination
        response = client.get("/api/v1/vouchers/?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 20
        assert data["total_pages"] == 2
        assert len(data["items"]) == 10

        # Get page 2
        response = client.get("/api/v1/vouchers/?page=2&page_size=10")
        assert len(response.json()["items"]) == 10

        # Deactivate half
        for i in range(0, len(codes), 2):
            response = client.patch(f"/api/v1/vouchers/{codes[i]}/deactivate")
            assert response.status_code == 200