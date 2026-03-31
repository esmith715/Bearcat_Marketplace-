import pytest
from uuid import uuid4

from server.services import listings_service
from server.schemas.listing import ListingCreate, ListingUpdate, ListingType, ListingStatus


#=======================#
# create_listing Tests  #
#=======================#
class TestCreateListing:

    async def test_create_misc_listing_success(self, test_conn, registered_user):
        listing = await listings_service.create_listing(
            test_conn,
            ListingCreate(
                type=ListingType.misc,
                title="Old Desk Chair",
                description="Slightly worn",
                price_cents=2500,
                item_condition="Good"
            ),
            registered_user.id
        )

        assert listing.title == "Old Desk Chair"
        assert listing.price_cents == 2500
        assert listing.type == ListingType.misc
        assert listing.status == ListingStatus.active
        assert listing.created_by == registered_user.id

    async def test_create_book_listing_success(self, test_conn, registered_user, sample_book, sample_course):
        listing = await listings_service.create_listing(
            test_conn,
            ListingCreate(
                type=ListingType.book,
                title="Clean Code Textbook",
                price_cents=3999,
                book_id=sample_book["id"],
                course_id=sample_course["id"],
                isbn="9780132350884"
            ),
            registered_user.id
        )

        assert listing.type == ListingType.book
        assert listing.book_id == sample_book["id"]
        assert listing.course_id == sample_course["id"]
        assert listing.isbn == "9780132350884"

    async def test_create_furniture_listing_success(self, test_conn, registered_user):
        listing = await listings_service.create_listing(
            test_conn,
            ListingCreate(
                type=ListingType.furniture,
                title="Standing Desk",
                price_cents=15000,
                measurements="60in x 30in"
            ),
            registered_user.id
        )

        assert listing.type == ListingType.furniture
        assert listing.measurements == "60in x 30in"

    async def test_create_listing_invalid_book_id(self, test_conn, registered_user):
        with pytest.raises(ValueError, match="Book ID not found"):
            await listings_service.create_listing(
                test_conn,
                ListingCreate(
                    type=ListingType.book,
                    title="Some Book",
                    price_cents=1000,
                    book_id=uuid4()  # non-existent
                ),
                registered_user.id
            )

    async def test_create_listing_invalid_course_id(self, test_conn, registered_user):
        with pytest.raises(ValueError, match="Course ID not found"):
            await listings_service.create_listing(
                test_conn,
                ListingCreate(
                    type=ListingType.book,
                    title="Some Book",
                    price_cents=1000,
                    course_id=uuid4()  # non-existent
                ),
                registered_user.id
            )

    async def test_create_listing_status_defaults_to_active(self, test_conn, registered_user):
        listing = await listings_service.create_listing(
            test_conn,
            ListingCreate(
                type=ListingType.misc,
                title="Random Item",
                price_cents=500
            ),
            registered_user.id
        )

        assert listing.status == ListingStatus.active

    async def test_create_listing_zero_price(self, test_conn, registered_user):
        """Free listings should be allowed."""
        listing = await listings_service.create_listing(
            test_conn,
            ListingCreate(
                type=ListingType.misc,
                title="Free Stuff",
                price_cents=0
            ),
            registered_user.id
        )

        assert listing.price_cents == 0


#=========================#
# get_listing_by_id Tests #
#=========================#
class TestGetListingById:

    async def test_get_listing_by_id_success(self, test_conn, sample_listing):
        listing = await listings_service.get_listing_by_id(test_conn, sample_listing.id)

        assert listing.id == sample_listing.id
        assert listing.title == sample_listing.title

    async def test_get_listing_by_id_not_found(self, test_conn):
        with pytest.raises(ValueError, match="Listing not found"):
            await listings_service.get_listing_by_id(test_conn, uuid4())


#=========================#
# get_all_listings Tests  #
#=========================#
class TestGetAllListings:

    async def test_get_all_listings_returns_list(self, test_conn, sample_listing):
        listings = await listings_service.get_all_listings(test_conn)

        assert isinstance(listings, list)
        assert len(listings) >= 1

    async def test_get_all_listings_empty(self, test_conn):
        listings = await listings_service.get_all_listings(test_conn)
        assert listings == []

    async def test_get_all_listings_filter_by_type(self, test_conn, registered_user):
        # Create one book listing and one misc listing
        await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.book, title="A Book", price_cents=1000),
            registered_user.id
        )
        await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="A Misc Item", price_cents=500),
            registered_user.id
        )

        book_listings = await listings_service.get_all_listings(test_conn, listing_type=ListingType.book)
        assert all(l.type == ListingType.book for l in book_listings)

        misc_listings = await listings_service.get_all_listings(test_conn, listing_type=ListingType.misc)
        assert all(l.type == ListingType.misc for l in misc_listings)

    async def test_get_all_listings_filter_by_status(self, test_conn, registered_user):
        listing = await listings_service.create_listing(
            test_conn,
            ListingCreate(type=ListingType.misc, title="Active Item", price_cents=100),
            registered_user.id
        )
        # Mark it as sold
        await listings_service.update_listing(
            test_conn,
            listing.id,
            ListingUpdate(status=ListingStatus.sold)
        )

        active = await listings_service.get_all_listings(test_conn, status=ListingStatus.active)
        sold = await listings_service.get_all_listings(test_conn, status=ListingStatus.sold)

        assert all(l.status == ListingStatus.active for l in active)
        assert any(l.id == listing.id for l in sold)

    async def test_get_all_listings_pagination(self, test_conn, registered_user):
        # Create 4 listings
        for i in range(4):
            await listings_service.create_listing(
                test_conn,
                ListingCreate(type=ListingType.misc, title=f"Item {i}", price_cents=i * 100),
                registered_user.id
            )

        page_one = await listings_service.get_all_listings(test_conn, skip=0, limit=2)
        page_two = await listings_service.get_all_listings(test_conn, skip=2, limit=2)

        assert len(page_one) == 2
        assert len(page_two) == 2

        page_one_ids = {l.id for l in page_one}
        page_two_ids = {l.id for l in page_two}
        assert page_one_ids.isdisjoint(page_two_ids)


#======================#
# update_listing Tests #
#======================#
class TestUpdateListing:

    async def test_update_title(self, test_conn, sample_listing):
        updated = await listings_service.update_listing(
            test_conn,
            sample_listing.id,
            ListingUpdate(title="Updated Title")
        )

        assert updated.title == "Updated Title"
        assert updated.price_cents == sample_listing.price_cents  # unchanged

    async def test_update_price(self, test_conn, sample_listing):
        updated = await listings_service.update_listing(
            test_conn,
            sample_listing.id,
            ListingUpdate(price_cents=9999)
        )

        assert updated.price_cents == 9999

    async def test_update_status(self, test_conn, sample_listing):
        updated = await listings_service.update_listing(
            test_conn,
            sample_listing.id,
            ListingUpdate(status=ListingStatus.inactive)
        )

        assert updated.status == ListingStatus.inactive

    async def test_update_with_valid_book_id(self, test_conn, sample_listing, sample_book):
        updated = await listings_service.update_listing(
            test_conn,
            sample_listing.id,
            ListingUpdate(book_id=sample_book["id"])
        )

        assert updated.book_id == sample_book["id"]

    async def test_update_with_invalid_book_id(self, test_conn, sample_listing):
        with pytest.raises(ValueError, match="Book ID not found"):
            await listings_service.update_listing(
                test_conn,
                sample_listing.id,
                ListingUpdate(book_id=uuid4())
            )

    async def test_update_with_valid_course_id(self, test_conn, sample_listing, sample_course):
        updated = await listings_service.update_listing(
            test_conn,
            sample_listing.id,
            ListingUpdate(course_id=sample_course["id"])
        )

        assert updated.course_id == sample_course["id"]

    async def test_update_with_invalid_course_id(self, test_conn, sample_listing):
        with pytest.raises(ValueError, match="Course ID not found"):
            await listings_service.update_listing(
                test_conn,
                sample_listing.id,
                ListingUpdate(course_id=uuid4())
            )

    async def test_update_sold_to_valid_user(self, test_conn, sample_listing, registered_user):
        updated = await listings_service.update_listing(
            test_conn,
            sample_listing.id,
            ListingUpdate(sold_to=registered_user.id)
        )

        assert updated.sold_to == registered_user.id

    async def test_update_sold_to_invalid_user(self, test_conn, sample_listing):
        with pytest.raises(ValueError, match="sold_to User ID not found"):
            await listings_service.update_listing(
                test_conn,
                sample_listing.id,
                ListingUpdate(sold_to=uuid4())
            )

    async def test_update_no_fields_returns_existing_listing(self, test_conn, sample_listing):
        result = await listings_service.update_listing(
            test_conn,
            sample_listing.id,
            ListingUpdate()
        )

        assert result.id == sample_listing.id
        assert result.title == sample_listing.title

    async def test_update_nonexistent_listing(self, test_conn):
        with pytest.raises(ValueError, match="Failed to update listing"):
            await listings_service.update_listing(
                test_conn,
                uuid4(),
                ListingUpdate(title="Ghost Listing")
            )


#======================#
# delete_listing Tests #
#======================#
class TestDeleteListing:

    async def test_delete_listing_success(self, test_conn, sample_listing):
        result = await listings_service.delete_listing(test_conn, sample_listing.id)
        assert result is True

    async def test_delete_listing_not_found(self, test_conn):
        result = await listings_service.delete_listing(test_conn, uuid4())
        assert result is False

    async def test_delete_listing_no_longer_retrievable(self, test_conn, sample_listing):
        await listings_service.delete_listing(test_conn, sample_listing.id)

        with pytest.raises(ValueError, match="Listing not found"):
            await listings_service.get_listing_by_id(test_conn, sample_listing.id)