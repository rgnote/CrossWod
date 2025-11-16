import pytest


class TestExercisesAPI:
    """Test exercise management endpoints."""

    # Positive test cases
    def test_get_all_exercises(self, client):
        """Test getting all exercises."""
        response = client.get("/api/exercises/")
        assert response.status_code == 200
        exercises = response.json()
        assert len(exercises) >= 5  # We seeded 5 exercises

    def test_get_exercises_filtered_by_category(self, client):
        """Test filtering exercises by category."""
        response = client.get("/api/exercises/?category=push")
        assert response.status_code == 200
        exercises = response.json()
        assert len(exercises) > 0
        for ex in exercises:
            assert ex["category"] == "push"

    def test_get_exercises_search_by_name(self, client):
        """Test searching exercises by name."""
        response = client.get("/api/exercises/?search=Bench")
        assert response.status_code == 200
        exercises = response.json()
        assert len(exercises) >= 1
        assert any("Bench" in ex["name"] for ex in exercises)

    def test_get_single_exercise(self, client):
        """Test getting a single exercise."""
        # First get all to find an ID
        all_response = client.get("/api/exercises/")
        exercise_id = all_response.json()[0]["id"]

        response = client.get(f"/api/exercises/{exercise_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "category" in data
        assert "muscle_groups" in data

    def test_get_categories(self, client):
        """Test getting all exercise categories."""
        response = client.get("/api/exercises/categories")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert "push" in categories
        assert "pull" in categories
        assert "legs" in categories

    def test_get_muscle_groups(self, client):
        """Test getting all muscle groups."""
        response = client.get("/api/exercises/muscle-groups")
        assert response.status_code == 200
        muscle_groups = response.json()
        assert isinstance(muscle_groups, list)
        assert "chest" in muscle_groups
        assert "back" in muscle_groups
        assert "quadriceps" in muscle_groups

    def test_create_custom_exercise(self, client, sample_user):
        """Test creating a custom exercise."""
        response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "Custom Exercise",
                "description": "My custom exercise",
                "category": "push",
                "muscle_groups": ["chest", "shoulders"],
                "equipment": "dumbbell"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Custom Exercise"
        assert data["is_custom"] is True
        assert data["created_by"] == sample_user["id"]
        assert data["muscle_groups"] == ["chest", "shoulders"]

    def test_update_custom_exercise(self, client, sample_user):
        """Test updating a custom exercise."""
        # Create first
        create_response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "To Update",
                "category": "legs",
                "muscle_groups": ["quadriceps"],
                "equipment": "barbell"
            }
        )
        exercise_id = create_response.json()["id"]

        # Update
        response = client.put(
            f"/api/exercises/{exercise_id}?user_id={sample_user['id']}",
            json={
                "name": "Updated Exercise",
                "category": "legs",
                "muscle_groups": ["quadriceps", "glutes"],
                "equipment": "machine"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Exercise"
        assert "glutes" in data["muscle_groups"]

    def test_delete_custom_exercise(self, client, sample_user):
        """Test deleting a custom exercise."""
        # Create first
        create_response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "To Delete",
                "category": "core",
                "muscle_groups": ["core"]
            }
        )
        exercise_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/api/exercises/{exercise_id}?user_id={sample_user['id']}")
        assert response.status_code == 200

        # Verify deleted
        get_response = client.get(f"/api/exercises/{exercise_id}")
        assert get_response.status_code == 404

    def test_filter_exercises_by_user_custom_only(self, client, sample_user):
        """Test that user sees only their custom exercises plus defaults."""
        # Create custom exercise
        client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "User Custom",
                "category": "push",
                "muscle_groups": ["chest"]
            }
        )

        response = client.get(f"/api/exercises/?user_id={sample_user['id']}")
        exercises = response.json()

        # Should include default exercises and user's custom exercise
        custom_exercises = [ex for ex in exercises if ex["is_custom"]]
        assert len(custom_exercises) == 1
        assert custom_exercises[0]["created_by"] == sample_user["id"]

    # Negative test cases
    def test_get_nonexistent_exercise(self, client):
        """Test getting exercise that doesn't exist."""
        response = client.get("/api/exercises/99999")
        assert response.status_code == 404

    def test_create_exercise_missing_name(self, client, sample_user):
        """Test creating exercise without name."""
        response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "category": "push",
                "muscle_groups": ["chest"]
            }
        )
        assert response.status_code == 422

    def test_create_exercise_missing_category(self, client, sample_user):
        """Test creating exercise without category."""
        response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "Test",
                "muscle_groups": ["chest"]
            }
        )
        assert response.status_code == 422

    def test_create_exercise_empty_muscle_groups(self, client, sample_user):
        """Test creating exercise with empty muscle groups."""
        response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "Test",
                "category": "push",
                "muscle_groups": []
            }
        )
        # This should still work - empty list is valid
        assert response.status_code == 200

    def test_create_exercise_missing_user_id(self, client):
        """Test creating exercise without user_id."""
        response = client.post(
            "/api/exercises/",
            json={
                "name": "Test",
                "category": "push",
                "muscle_groups": ["chest"]
            }
        )
        assert response.status_code == 422  # Missing required query param

    def test_update_non_custom_exercise(self, client, sample_user):
        """Test updating a non-custom (seeded) exercise."""
        # Get a seeded exercise
        all_response = client.get("/api/exercises/?include_custom=false")
        exercise_id = all_response.json()[0]["id"]

        response = client.put(
            f"/api/exercises/{exercise_id}?user_id={sample_user['id']}",
            json={
                "name": "Hacked Name",
                "category": "push",
                "muscle_groups": ["chest"]
            }
        )
        assert response.status_code == 403  # Forbidden

    def test_delete_non_custom_exercise(self, client, sample_user):
        """Test deleting a non-custom exercise."""
        all_response = client.get("/api/exercises/?include_custom=false")
        exercise_id = all_response.json()[0]["id"]

        response = client.delete(f"/api/exercises/{exercise_id}?user_id={sample_user['id']}")
        assert response.status_code == 403

    def test_update_other_users_exercise(self, client, sample_user):
        """Test updating another user's custom exercise."""
        # Create exercise for first user
        create_response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "User1 Exercise",
                "category": "push",
                "muscle_groups": ["chest"]
            }
        )
        exercise_id = create_response.json()["id"]

        # Create second user
        user2_response = client.post("/api/users/", json={"name": "User 2"})
        user2_id = user2_response.json()["id"]

        # Try to update with second user
        response = client.put(
            f"/api/exercises/{exercise_id}?user_id={user2_id}",
            json={
                "name": "Stolen",
                "category": "push",
                "muscle_groups": ["chest"]
            }
        )
        assert response.status_code == 403

    def test_delete_other_users_exercise(self, client, sample_user):
        """Test deleting another user's custom exercise."""
        # Create exercise for first user
        create_response = client.post(
            f"/api/exercises/?user_id={sample_user['id']}",
            json={
                "name": "User1 Exercise",
                "category": "legs",
                "muscle_groups": ["quadriceps"]
            }
        )
        exercise_id = create_response.json()["id"]

        # Create second user
        user2_response = client.post("/api/users/", json={"name": "User 2"})
        user2_id = user2_response.json()["id"]

        # Try to delete with second user
        response = client.delete(f"/api/exercises/{exercise_id}?user_id={user2_id}")
        assert response.status_code == 403

    def test_filter_nonexistent_category(self, client):
        """Test filtering by category that doesn't exist."""
        response = client.get("/api/exercises/?category=nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_search_no_results(self, client):
        """Test searching with no matching results."""
        response = client.get("/api/exercises/?search=XYZ123NOTFOUND")
        assert response.status_code == 200
        assert response.json() == []
