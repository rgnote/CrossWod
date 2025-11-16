import pytest
from io import BytesIO


class TestUsersAPI:
    """Test user management endpoints."""

    # Positive test cases
    def test_create_user_success(self, client):
        """Test successful user creation."""
        response = client.post("/api/users/", json={"name": "John Doe"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert "id" in data
        assert "created_at" in data
        assert "last_active" in data
        assert data["has_profile_picture"] is False

    def test_get_users_empty(self, client):
        """Test getting users when none exist."""
        response = client.get("/api/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_users_with_data(self, client, sample_user):
        """Test getting users list."""
        response = client.get("/api/users/")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 1
        assert users[0]["name"] == sample_user["name"]

    def test_get_single_user(self, client, sample_user):
        """Test getting a single user by ID."""
        response = client.get(f"/api/users/{sample_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user["id"]
        assert data["name"] == sample_user["name"]

    def test_update_user_name(self, client, sample_user):
        """Test updating user name."""
        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["id"] == sample_user["id"]

    def test_delete_user(self, client, sample_user):
        """Test deleting a user."""
        response = client.delete(f"/api/users/{sample_user['id']}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify user is deleted
        response = client.get(f"/api/users/{sample_user['id']}")
        assert response.status_code == 404

    def test_create_multiple_users(self, client):
        """Test creating multiple users."""
        names = ["Alice", "Bob", "Charlie"]
        for name in names:
            response = client.post("/api/users/", json={"name": name})
            assert response.status_code == 200

        response = client.get("/api/users/")
        users = response.json()
        assert len(users) == 3
        user_names = [u["name"] for u in users]
        for name in names:
            assert name in user_names

    def test_upload_profile_picture(self, client, sample_user):
        """Test uploading profile picture."""
        # Create a small test image
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        response = client.post(
            f"/api/users/{sample_user['id']}/profile-picture",
            files={"file": ("test.png", img_bytes, "image/png")}
        )
        assert response.status_code == 200

        # Verify user now has profile picture
        user_response = client.get(f"/api/users/{sample_user['id']}")
        assert user_response.json()["has_profile_picture"] is True

    def test_get_profile_picture(self, client, sample_user):
        """Test retrieving profile picture."""
        # First upload
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        client.post(
            f"/api/users/{sample_user['id']}/profile-picture",
            files={"file": ("test.png", img_bytes, "image/png")}
        )

        # Then retrieve
        response = client.get(f"/api/users/{sample_user['id']}/profile-picture")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_delete_profile_picture(self, client, sample_user):
        """Test deleting profile picture."""
        # Upload first
        from PIL import Image
        img = Image.new('RGB', (50, 50), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        client.post(
            f"/api/users/{sample_user['id']}/profile-picture",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )

        # Delete
        response = client.delete(f"/api/users/{sample_user['id']}/profile-picture")
        assert response.status_code == 200

        # Verify deleted
        user_response = client.get(f"/api/users/{sample_user['id']}")
        assert user_response.json()["has_profile_picture"] is False

    # Negative test cases
    def test_create_user_empty_name(self, client):
        """Test creating user with empty name."""
        response = client.post("/api/users/", json={"name": ""})
        assert response.status_code == 422  # Validation error

    def test_create_user_missing_name(self, client):
        """Test creating user without name field."""
        response = client.post("/api/users/", json={})
        assert response.status_code == 422

    def test_create_user_name_too_long(self, client):
        """Test creating user with name exceeding max length."""
        long_name = "A" * 101  # Max is 100
        response = client.post("/api/users/", json={"name": long_name})
        assert response.status_code == 422

    def test_get_nonexistent_user(self, client):
        """Test getting a user that doesn't exist."""
        response = client.get("/api/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_user(self, client):
        """Test updating a user that doesn't exist."""
        response = client.put("/api/users/99999", json={"name": "New Name"})
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client):
        """Test deleting a user that doesn't exist."""
        response = client.delete("/api/users/99999")
        assert response.status_code == 404

    def test_upload_non_image_file(self, client, sample_user):
        """Test uploading non-image file as profile picture."""
        text_file = BytesIO(b"This is not an image")
        response = client.post(
            f"/api/users/{sample_user['id']}/profile-picture",
            files={"file": ("test.txt", text_file, "text/plain")}
        )
        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower()

    def test_get_profile_picture_none_exists(self, client, sample_user):
        """Test getting profile picture when none uploaded."""
        response = client.get(f"/api/users/{sample_user['id']}/profile-picture")
        assert response.status_code == 404

    def test_upload_profile_picture_nonexistent_user(self, client):
        """Test uploading profile picture for nonexistent user."""
        from PIL import Image
        img = Image.new('RGB', (50, 50), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        response = client.post(
            "/api/users/99999/profile-picture",
            files={"file": ("test.png", img_bytes, "image/png")}
        )
        assert response.status_code == 404

    def test_create_user_with_special_characters(self, client):
        """Test creating user with special characters in name."""
        response = client.post("/api/users/", json={"name": "José María"})
        assert response.status_code == 200
        assert response.json()["name"] == "José María"

    def test_update_user_with_empty_name(self, client, sample_user):
        """Test updating user with empty name."""
        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={"name": ""}
        )
        assert response.status_code == 422
