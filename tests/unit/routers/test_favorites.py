import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from server.main import app
from server.dependencies import get_current_user

def make_mock_listing(**overrides):
    defaults = {
        "id": uuid4(),
        "title": "Test Listing",
        "type": "misc",
        "status": "active",
        "price_cents": 2500,
        "created_by": uuid4(),
        "description": None,
        "item_condition": None,
        "book_id": None,
        "course_id": None,
        "isbn": None,
        "measurements": None,
        "sold_to": None,
        "image_url": None,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock

# ================================
# POST /favorites/{listing_id}
# ================================
class TestFavoriteListing:

    
    async def test_favorite_listing_success(self, client, mock_conn, make_mock_user):
        """Authenticated user should be able to favorite an existing listing"""
        mock_user = make_mock_user()
        mock_listing = make_mock_listing()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get, \
             patch("server.routers.favorites.favorites_service.add_favorite", new_callable=AsyncMock) as mock_add:

            mock_get.return_value = mock_listing
            mock_add.return_value = None

            response = await client.post(f"/favorites/{mock_listing.id}")

            assert response.status_code == 204
            mock_add.assert_called_once_with(mock_conn, mock_user.id, mock_listing.id)

        app.dependency_overrides.clear()

    
    async def test_favorite_listing_not_found(self, client, mock_conn, make_mock_user):
        """Should return 404 if the listing does not exist"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            response = await client.post(f"/favorites/{uuid4()}")

            assert response.status_code == 404
            assert response.json()["detail"] == "Listing not found"

        app.dependency_overrides.clear()

    
    async def test_favorite_listing_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.post(f"/favorites/{uuid4()}")
        assert response.status_code == 401

    
    async def test_favorite_listing_does_not_call_add_when_listing_missing(self, client, mock_conn, make_mock_user):
        """add_favorite should never be called if the listing lookup fails"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.listings_service.get_listing_by_id", new_callable=AsyncMock) as mock_get, \
             patch("server.routers.favorites.favorites_service.add_favorite", new_callable=AsyncMock) as mock_add:

            mock_get.return_value = None

            await client.post(f"/favorites/{uuid4()}")

            mock_add.assert_not_called()

        app.dependency_overrides.clear()

# ================================
# DELETE /favorites/{listing_id}
# ================================
class TestUnfavoriteListing:

    
    async def test_unfavorite_listing_success(self, client, mock_conn, make_mock_user):
        """Authenticated user should be able to unfavorite a listing"""
        mock_user = make_mock_user()
        listing_id = uuid4()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.favorites_service.remove_favorite", new_callable=AsyncMock) as mock_remove:
            mock_remove.return_value = True

            response = await client.delete(f"/favorites/{listing_id}")

            assert response.status_code == 204
            mock_remove.assert_called_once_with(mock_conn, mock_user.id, listing_id)

        app.dependency_overrides.clear()

    
    async def test_unfavorite_listing_not_favorited_still_returns_204(self, client, mock_conn, make_mock_user):
        """
        Removing a non-existent favorite should still return 204.
        The router does not check the bool return from remove_favorite.
        """
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.favorites_service.remove_favorite", new_callable=AsyncMock) as mock_remove:
            mock_remove.return_value = False  # nothing was deleted

            response = await client.delete(f"/favorites/{uuid4()}")

            assert response.status_code == 204

        app.dependency_overrides.clear()

    
    async def test_unfavorite_listing_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.delete(f"/favorites/{uuid4()}")
        assert response.status_code == 401

# ================================
# GET /favorites/me
# ================================
class TestGetMyFavorites:

    
    async def test_get_my_favorites_success(self, client, mock_conn, make_mock_user):
        """Should return the current user's favorited listings"""
        mock_user = make_mock_user()
        mock_listings = [make_mock_listing(), make_mock_listing()]
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.favorites_service.get_favorite_listings_by_user_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_listings

            response = await client.get("/favorites/me")

            assert response.status_code == 200
            mock_get.assert_called_once_with(mock_conn, mock_user.id)

        app.dependency_overrides.clear()

    
    async def test_get_my_favorites_empty(self, client, mock_conn, make_mock_user):
        """User with no favorites should get an empty list"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.favorites_service.get_favorite_listings_by_user_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            response = await client.get("/favorites/me")

            assert response.status_code == 200
            assert response.json() == []

        app.dependency_overrides.clear()

    
    async def test_get_my_favorites_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.get("/favorites/me")
        assert response.status_code == 401

# ================================
# GET /favorites/me/ids
# ================================
class TestGetMyFavoriteIds:

    
    async def test_get_my_favorite_ids_success(self, client, mock_conn, make_mock_user):
        """Should return a list of UUIDs for the user's favorited listings"""
        mock_user = make_mock_user()
        fake_ids = [uuid4(), uuid4()]
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.favorites_service.get_favorite_listing_ids_by_user_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = fake_ids

            response = await client.get("/favorites/me/ids")

            assert response.status_code == 200
            assert len(response.json()) == 2
            mock_get.assert_called_once_with(mock_conn, mock_user.id)

        app.dependency_overrides.clear()

    
    async def test_get_my_favorite_ids_empty(self, client, mock_conn, make_mock_user):
        """User with no favorites should get an empty list of IDs"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.favorites.favorites_service.get_favorite_listing_ids_by_user_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            response = await client.get("/favorites/me/ids")

            assert response.status_code == 200
            assert response.json() == []

        app.dependency_overrides.clear()

    
    async def test_get_my_favorite_ids_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.get("/favorites/me/ids")
        assert response.status_code == 401