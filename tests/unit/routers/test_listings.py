import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from server.main import app
from server.dependencies import get_current_user
from server.schemas.listing import ListingType, ListingStatus

def make_mock_listing(**overrides):
    defaults = {
        "id": uuid4(),
        "title": "Test Listing",
        "type": ListingType.misc,
        "status": ListingStatus.active,
        "price_cents": 2500,
        "created_by": uuid4(),
        "description": None,
        "item_condition": None,
        "book_id": None,
        "course_id": None,
        "isbn": None,
        "measurements": None,
        "sold_to": None,
        "image_path": None,
    }
    defaults.update(overrides)

    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)

    mock.model_dump = lambda: defaults
    return mock

# ====================
# POST /listings/
# ====================
class TestCreateListing:

    
    async def test_create_listing_success(self, client, mock_conn, make_mock_user):
        """Authenticated user should be able to create a listing"""
        mock_user = make_mock_user()
        mock_listing = make_mock_listing(created_by=mock_user.id)

        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.create_listing", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_listing

            response = await client.post("/listings/", json={
                "type": "misc",
                "title": "Test Listing",
                "price_cents": 2500
            })

            assert response.status_code == 201

        app.dependency_overrides.clear()

    
    async def test_create_listing_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.post("/listings/", json={
            "type": "misc",
            "title": "Test Listing",
            "price_cents": 2500
        })
        assert response.status_code == 401

    
    async def test_create_listing_value_error(self, client, mock_conn, make_mock_user):
        """Service raising ValueError should return 400"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.create_listing", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValueError("Invalid listing data")

            response = await client.post("/listings/", json={
                "type": "misc",
                "title": "Bad Listing",
                "price_cents": 100
            })

            assert response.status_code == 400

        app.dependency_overrides.clear()

# ====================
# GET /listings/
# ====================
class TestGetListing:

    
    async def test_get_listing_success(self, client, mock_conn):
        """Should return a listing by ID"""
        mock_listing = make_mock_listing()

        with patch("server.routers.listings.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_listing

            response = await client.get("/listings/", params={"listing_id": str(mock_listing.id)})

            assert response.status_code == 200

    
    async def test_get_listing_not_found(self, client, mock_conn):
        """Non-existent listing should return 404"""
        with patch("server.routers.listings.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = ValueError("Listing not found")

            response = await client.get("/listings/", params={"listing_id": str(uuid4())})

            assert response.status_code == 404

# ====================
# GET /listings/me
# ====================
class TestGetMyListings:

    
    async def test_get_my_listings_success(self, client, mock_conn, make_mock_user):
        """Should return listings for the logged in user"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.get_listings_by_user_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [make_mock_listing(created_by=mock_user.id)]

            response = await client.get("/listings/me")

            assert response.status_code == 200

        app.dependency_overrides.clear()

    
    async def test_get_my_listings_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.get("/listings/me")
        assert response.status_code == 401

# ====================
# PATCH /listings/
# ====================
class TestUpdateListing:

    
    async def test_update_listing_success(self, client, mock_conn, make_mock_user):
        """Owner should be able to update their listing"""
        mock_user = make_mock_user()
        mock_listing = make_mock_listing(created_by=mock_user.id)
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get, \
             patch("server.routers.listings.listings_service.update_listing", new_callable=AsyncMock) as mock_update, \
             patch("server.routers.listings.favorites_service.get_users_who_favorited_listing", new_callable=AsyncMock) as mock_favs:

            mock_get.return_value = mock_listing
            mock_update.return_value = mock_listing
            mock_favs.return_value = []

            response = await client.patch(f"/listings/{mock_listing.id}", json={
                "title": "Updated Title"
            })

            assert response.status_code == 200

        app.dependency_overrides.clear()

    
    async def test_update_listing_not_owner(self, client, mock_conn, make_mock_user):
        """Non-owner should get 401"""
        mock_user = make_mock_user()
        mock_listing = make_mock_listing(created_by=uuid4())  # different owner
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_listing

            response = await client.patch(f"/listings/{mock_listing.id}", json={
                "title": "Sneaky Update"
            })

            assert response.status_code == 401

        app.dependency_overrides.clear()

    
    async def test_update_listing_not_found(self, client, mock_conn, make_mock_user):
        """Non-existent listing should return 404"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            response = await client.patch(f"/listings/{uuid4()}", json={
                "title": "Ghost Update"
            })

            assert response.status_code == 404

        app.dependency_overrides.clear()

# ====================
# DELETE /listings/
# ====================
class TestDeleteListing:

    
    async def test_delete_listing_success(self, client, mock_conn, make_mock_user):
        """Owner should be able to delete their listing"""
        mock_user = make_mock_user()
        mock_listing = make_mock_listing(created_by=mock_user.id)
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get, \
             patch("server.routers.listings.listings_service.delete_listing", new_callable=AsyncMock) as mock_delete:

            mock_get.return_value = mock_listing
            mock_delete.return_value = True

            response = await client.delete(f"/listings/{mock_listing.id}")

            assert response.status_code == 204

        app.dependency_overrides.clear()

    
    async def test_delete_listing_not_owner(self, client, mock_conn, make_mock_user):
        """Non-owner should get 401"""
        mock_user = make_mock_user()
        mock_listing = make_mock_listing(created_by=uuid4())
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.listings.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_listing

            response = await client.delete(f"/listings/{mock_listing.id}")

            assert response.status_code == 401

        app.dependency_overrides.clear()