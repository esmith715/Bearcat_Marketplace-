import pytest
from server.services import users_service
from server.schemas.user import UserRole, UserUpdateRequest
from server.schemas.auth import UserRegister
from uuid import uuid4


#======================#
# register_user Tests  #
#======================#
class TestRegisterUser:

    async def test_register_user_success(self, test_conn):
        registration_info = UserRegister(
            email="newuser@mail.uc.edu",
            username="newuser",
            password="SecurePassword123!"
        )
        user = await users_service.register_user(test_conn, registration_info)

        assert user.email == "newuser@mail.uc.edu"
        assert user.username == "newuser"
        assert user.role == UserRole.student
        assert user.is_email_verified is False
        assert user.admin_approved is False
        assert user.password_hash != "SecurePassword123!"  # must be hashed

    async def test_register_user_invalid_email_domain(self, test_conn):
        registration_info = UserRegister(
            email="newuser@gmail.com",
            username="newuser",
            password="SecurePassword123!"
        )
        with pytest.raises(ValueError, match="must be a valid @mail.uc.edu"):
            await users_service.register_user(test_conn, registration_info)

    async def test_register_user_duplicate_email(self, test_conn, registered_user):
        duplicate = UserRegister(
            email=registered_user.email,
            username="differentusername",
            password="SecurePassword123!"
        )
        with pytest.raises(ValueError, match="already exists"):
            await users_service.register_user(test_conn, duplicate)

    async def test_register_user_duplicate_username(self, test_conn, registered_user):
        duplicate = UserRegister(
            email="different@mail.uc.edu",
            username=registered_user.username,
            password="SecurePassword123!"
        )
        with pytest.raises(ValueError, match="already exists"):
            await users_service.register_user(test_conn, duplicate)


#=========================#
# get_user_by_email Tests #
#=========================#
class TestGetUserByEmail:

    async def test_get_user_by_email_success(self, test_conn, registered_user):
        user = await users_service.get_user_by_email(test_conn, registered_user.email)

        assert user.email == registered_user.email
        assert user.id == registered_user.id

    async def test_get_user_by_email_not_found(self, test_conn):
        with pytest.raises(ValueError, match="Email not found"):
            await users_service.get_user_by_email(test_conn, "ghost@mail.uc.edu")


#============================#
# get_user_by_username Tests #
#============================#
class TestGetUserByUsername:

    async def test_get_user_by_username_success(self, test_conn, registered_user):
        user = await users_service.get_user_by_username(test_conn, registered_user.username)

        assert user.username == registered_user.username
        assert user.id == registered_user.id

    async def test_get_user_by_username_not_found(self, test_conn):
        with pytest.raises(ValueError, match="Username not found"):
            await users_service.get_user_by_username(test_conn, "ghostuser")


#======================#
# get_user_by_id Tests #
#======================#
class TestGetUserById:

    async def test_get_user_by_id_success(self, test_conn, registered_user):
        user = await users_service.get_user_by_id(test_conn, registered_user.id)

        assert user.id == registered_user.id
        assert user.email == registered_user.email

    async def test_get_user_by_id_not_found(self, test_conn):
        with pytest.raises(ValueError, match="User ID not found"):
            await users_service.get_user_by_id(test_conn, uuid4())


#=====================#
# get_all_users Tests #
#=====================#
class TestGetAllUsers:

    async def test_get_all_users_returns_list(self, test_conn, registered_user):
        users = await users_service.get_all_users(test_conn)

        assert isinstance(users, list)
        assert len(users) >= 1

    async def test_get_all_users_skip_and_limit(self, test_conn):
        # Register 3 users
        for i in range(3):
            await users_service.register_user(test_conn, UserRegister(
                email=f"user{i}@mail.uc.edu",
                username=f"user{i}",
                password="SecurePassword123!"
            ))

        page_one = await users_service.get_all_users(test_conn, skip=0, limit=2)
        page_two = await users_service.get_all_users(test_conn, skip=2, limit=2)

        assert len(page_one) == 2
        assert len(page_two) >= 1
        # No overlap between pages
        page_one_ids = {u.id for u in page_one}
        page_two_ids = {u.id for u in page_two}
        assert page_one_ids.isdisjoint(page_two_ids)

    async def test_get_all_users_empty(self, test_conn):
        users = await users_service.get_all_users(test_conn)
        assert users == []


#===================#
# update_user Tests #
#===================#
class TestUpdateUser:

    async def test_update_username(self, test_conn, registered_user):
        update_data = UserUpdateRequest(username="updatedusername")
        updated = await users_service.update_user(test_conn, registered_user.id, update_data)

        assert updated.username == "updatedusername"
        assert updated.email == registered_user.email  # unchanged

    async def test_update_email(self, test_conn, registered_user):
        update_data = UserUpdateRequest(email="updated@mail.uc.edu")
        updated = await users_service.update_user(test_conn, registered_user.id, update_data)

        assert updated.email == "updated@mail.uc.edu"

    async def test_update_invalid_email_domain(self, test_conn, registered_user):
        update_data = UserUpdateRequest(email="updated@gmail.com")

        with pytest.raises(ValueError, match="must be a valid @mail.uc.edu"):
            await users_service.update_user(test_conn, registered_user.id, update_data)

    async def test_update_no_fields_returns_existing_user(self, test_conn, registered_user):
        update_data = UserUpdateRequest()
        result = await users_service.update_user(test_conn, registered_user.id, update_data)

        assert result.id == registered_user.id

    async def test_update_duplicate_email_raises(self, test_conn, registered_user):
        # Create a second user
        other = await users_service.register_user(test_conn, UserRegister(
            email="other@mail.uc.edu",
            username="otheruser",
            password="SecurePassword123!"
        ))

        # Try to steal registered_user's email
        update_data = UserUpdateRequest(email=registered_user.email)

        with pytest.raises(ValueError, match="already exists"):
            await users_service.update_user(test_conn, other.id, update_data)


#===================#
# delete_user Tests #
#===================#
class TestDeleteUser:

    async def test_delete_user_success(self, test_conn, registered_user):
        result = await users_service.delete_user(test_conn, registered_user.id)
        assert result is True

    async def test_delete_user_not_found(self, test_conn):
        result = await users_service.delete_user(test_conn, uuid4())
        assert result is False

    async def test_delete_user_no_longer_retrievable(self, test_conn, registered_user):
        await users_service.delete_user(test_conn, registered_user.id)

        with pytest.raises(ValueError, match="Email not found"):
            await users_service.get_user_by_email(test_conn, registered_user.email)