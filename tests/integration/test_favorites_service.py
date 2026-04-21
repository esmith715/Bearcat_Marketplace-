from uuid import uuid4

from server.services import favorites_service, users_service, listings_service
from server.schemas.auth import UserRegister
from server.schemas.listing import ListingCreate, ListingType

# ========================
# add_favorite Tests
# ========================

class TestAddFavorite:

    async def test_add_favorite_success(self, test_conn, registered_user, sample_listing):
        """User should be able to favorite a listing"""
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)

        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)
        assert sample_listing.id in ids

    async def test_add_favorite_idempotent(self, test_conn, registered_user, sample_listing):
        """Adding the same favorite twice should not raise an error (ON CONFLICT DO NOTHING)"""
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)

        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)
        assert ids.count(sample_listing.id) == 1

    async def test_add_multiple_favorites(self, test_conn, registered_user):
        """User should be able to favorite multiple listings"""
        listing_a = await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="Item A", price_cents=100),
            registered_user.id
        )
        listing_b = await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="Item B", price_cents=200),
            registered_user.id
        )

        await favorites_service.add_favorite(test_conn, registered_user.id, listing_a.id)
        await favorites_service.add_favorite(test_conn, registered_user.id, listing_b.id)

        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)
        assert listing_a.id in ids
        assert listing_b.id in ids

# ========================
# remove_favorite Tests
# ========================

class TestRemoveFavorite:

    async def test_remove_favorite_success(self, test_conn, registered_user, sample_listing):
        """Should remove a favorited listing and return True"""
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)

        result = await favorites_service.remove_favorite(test_conn, registered_user.id, sample_listing.id)
        assert result is True

        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)
        assert sample_listing.id not in ids

    async def test_remove_favorite_not_found_returns_false(self, test_conn, registered_user):
        """Removing a non-existent favorite should return False"""
        result = await favorites_service.remove_favorite(test_conn, registered_user.id, uuid4())
        assert result is False

    async def test_remove_favorite_does_not_affect_other_favorites(self, test_conn, registered_user):
        """Removing one favorite should not remove others"""
        listing_a = await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="Keep Me", price_cents=100),
            registered_user.id
        )
        listing_b = await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="Remove Me", price_cents=200),
            registered_user.id
        )

        await favorites_service.add_favorite(test_conn, registered_user.id, listing_a.id)
        await favorites_service.add_favorite(test_conn, registered_user.id, listing_b.id)

        await favorites_service.remove_favorite(test_conn, registered_user.id, listing_b.id)

        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)
        assert listing_a.id in ids
        assert listing_b.id not in ids

# ==========================================
# get_favorite_listings_by_user_id Tests
# ==========================================

class TestGetFavoriteListingsByUserId:

    async def test_returns_full_listing_objects(self, test_conn, registered_user, sample_listing):
        """Should return full Listing objects, not just IDs"""
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)

        listings = await favorites_service.get_favorite_listings_by_user_id(test_conn, registered_user.id)

        assert len(listings) == 1
        assert listings[0].id == sample_listing.id
        assert listings[0].title == sample_listing.title

    async def test_returns_empty_list_when_no_favorites(self, test_conn, registered_user):
        """User with no favorites should get an empty list"""
        listings = await favorites_service.get_favorite_listings_by_user_id(test_conn, registered_user.id)
        assert listings == []

    async def test_does_not_return_other_users_favorites(self, test_conn, registered_user, sample_listing):
        """Should only return favorites belonging to the requesting user"""
        other_user = await users_service.register_user(
            test_conn,
            UserRegister(
                email="other@mail.uc.edu",
                username="otheruser",
                password="SecurePassword123!"
            )
        )

        # Only other_user favorites the listing
        await favorites_service.add_favorite(test_conn, other_user.id, sample_listing.id)

        listings = await favorites_service.get_favorite_listings_by_user_id(test_conn, registered_user.id)
        assert listings == []

    async def test_returns_listings_ordered_by_most_recently_favorited(self, test_conn, registered_user):
        """Listings should be returned newest-favorited first"""
        listing_a = await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="First Favorited", price_cents=100),
            registered_user.id
        )
        listing_b = await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="Second Favorited", price_cents=200),
            registered_user.id
        )

        await favorites_service.add_favorite(test_conn, registered_user.id, listing_a.id)
        await favorites_service.add_favorite(test_conn, registered_user.id, listing_b.id)

        listings = await favorites_service.get_favorite_listings_by_user_id(test_conn, registered_user.id)

        # Most recently favorited (listing_b) should come first
        assert listings[0].id == listing_b.id
        assert listings[1].id == listing_a.id

# =============================================
# get_favorite_listing_ids_by_user_id Tests
# =============================================

class TestGetFavoriteListingIdsByUserId:

    async def test_returns_list_of_uuids(self, test_conn, registered_user, sample_listing):
        """Should return a list of UUIDs, not full objects"""
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)

        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)

        assert isinstance(ids, list)
        assert sample_listing.id in ids

    async def test_returns_empty_list_when_no_favorites(self, test_conn, registered_user):
        """No favorites should yield an empty list"""
        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)
        assert ids == []

    async def test_returns_only_own_favorite_ids(self, test_conn, registered_user, sample_listing):
        """Should not return IDs favorited by other users"""
        other_user = await users_service.register_user(
            test_conn,
            UserRegister(
                email="another@mail.uc.edu",
                username="anotheruser",
                password="SecurePassword123!"
            )
        )

        await favorites_service.add_favorite(test_conn, other_user.id, sample_listing.id)

        ids = await favorites_service.get_favorite_listing_ids_by_user_id(test_conn, registered_user.id)
        assert sample_listing.id not in ids

# =============================================
# get_users_who_favorited_listing Tests
# =============================================

class TestGetUsersWhoFavoritedListing:

    async def test_returns_users_who_favorited(self, test_conn, registered_user, sample_listing):
        """Should return all users who have favorited the given listing"""
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)

        users = await favorites_service.get_users_who_favorited_listing(test_conn, sample_listing.id)

        assert len(users) == 1
        assert users[0].id == registered_user.id

    async def test_returns_empty_list_when_no_favorites(self, test_conn, sample_listing):
        """Listing with no favorites should return empty list"""
        users = await favorites_service.get_users_who_favorited_listing(test_conn, sample_listing.id)
        assert users == []

    async def test_returns_multiple_users(self, test_conn, registered_user, sample_listing):
        """Should return all users who favorited, not just one"""
        other_user = await users_service.register_user(
            test_conn,
            UserRegister(
                email="third@mail.uc.edu",
                username="thirduser",
                password="SecurePassword123!"
            )
        )

        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)
        await favorites_service.add_favorite(test_conn, other_user.id, sample_listing.id)

        users = await favorites_service.get_users_who_favorited_listing(test_conn, sample_listing.id)
        user_ids = [u.id for u in users]

        assert registered_user.id in user_ids
        assert other_user.id in user_ids

    async def test_does_not_return_users_who_unfavorited(self, test_conn, registered_user, sample_listing):
        """Users who removed their favorite should not appear"""
        await favorites_service.add_favorite(test_conn, registered_user.id, sample_listing.id)
        await favorites_service.remove_favorite(test_conn, registered_user.id, sample_listing.id)

        users = await favorites_service.get_users_who_favorited_listing(test_conn, sample_listing.id)
        assert users == []

    async def test_returns_empty_for_nonexistent_listing(self, test_conn):
        """Non-existent listing ID should return empty list, not raise"""
        users = await favorites_service.get_users_who_favorited_listing(test_conn, uuid4())
        assert users == []