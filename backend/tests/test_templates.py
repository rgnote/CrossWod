import pytest
from datetime import datetime, timezone


class TestTemplatesAPI:
    """Test workout template endpoints."""

    # Positive test cases
    def test_create_template(self, client, sample_user):
        """Test creating a workout template."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Push Day",
                "description": "Chest and triceps focus",
                "category": "Push",
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "target_sets": 4,
                        "target_reps": "8-12",
                        "target_weight": 80,
                        "rest_seconds": 120
                    }
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Push Day"
        assert data["category"] == "Push"
        assert len(data["exercises"]) == 1
        assert data["exercises"][0]["target_sets"] == 4

    def test_get_templates(self, client, sample_user):
        """Test getting user's templates."""
        # Create a template first
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Test Template",
                "exercises": [
                    {"exercise_id": exercise_id, "order": 1}
                ]
            }
        )

        response = client.get(f"/api/templates/?user_id={sample_user['id']}")
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) == 1
        assert templates[0]["name"] == "Test Template"

    def test_get_single_template(self, client, sample_user):
        """Test getting a single template."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        create_response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Leg Day",
                "exercises": [
                    {"exercise_id": exercise_id, "order": 1}
                ]
            }
        )
        template_id = create_response.json()["id"]

        response = client.get(f"/api/templates/{template_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Leg Day"
        assert "exercises" in data

    def test_update_template(self, client, sample_user):
        """Test updating a template."""
        exercises_response = client.get("/api/exercises/")
        exercise_ids = [ex["id"] for ex in exercises_response.json()[:2]]

        create_response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Old Name",
                "exercises": [
                    {"exercise_id": exercise_ids[0], "order": 1}
                ]
            }
        )
        template_id = create_response.json()["id"]

        response = client.put(
            f"/api/templates/{template_id}",
            json={
                "name": "Updated Name",
                "description": "New description",
                "category": "Pull",
                "exercises": [
                    {"exercise_id": exercise_ids[0], "order": 1},
                    {"exercise_id": exercise_ids[1], "order": 2}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["category"] == "Pull"
        assert len(data["exercises"]) == 2

    def test_delete_template(self, client, sample_user):
        """Test deleting a template."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        create_response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "To Delete",
                "exercises": [{"exercise_id": exercise_id, "order": 1}]
            }
        )
        template_id = create_response.json()["id"]

        response = client.delete(f"/api/templates/{template_id}")
        assert response.status_code == 200

        # Verify deleted
        get_response = client.get(f"/api/templates/{template_id}")
        assert get_response.status_code == 404

    def test_start_workout_from_template(self, client, sample_user):
        """Test starting a workout from a template."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        create_response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Push Day",
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "target_sets": 3,
                        "target_weight": 100,
                        "rest_seconds": 90
                    }
                ]
            }
        )
        template_id = create_response.json()["id"]

        response = client.post(
            f"/api/templates/{template_id}/start?user_id={sample_user['id']}"
        )
        assert response.status_code == 200
        workout = response.json()
        assert workout["name"] == "Push Day"
        assert len(workout["exercises"]) == 1
        # Should have pre-populated sets
        assert len(workout["exercises"][0]["sets"]) == 3
        assert workout["exercises"][0]["sets"][0]["weight"] == 100

    def test_template_last_used_updates(self, client, sample_user):
        """Test that last_used timestamp updates when starting workout."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        create_response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Test",
                "exercises": [{"exercise_id": exercise_id, "order": 1}]
            }
        )
        template_id = create_response.json()["id"]
        assert create_response.json()["last_used"] is None

        # Start workout from template
        client.post(f"/api/templates/{template_id}/start?user_id={sample_user['id']}")

        # Check last_used is updated
        template_response = client.get(f"/api/templates/{template_id}")
        assert template_response.json()["last_used"] is not None

    def test_create_template_multiple_exercises(self, client, sample_user):
        """Test creating template with multiple exercises."""
        exercises_response = client.get("/api/exercises/")
        exercise_ids = [ex["id"] for ex in exercises_response.json()[:3]]

        response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Full Body",
                "exercises": [
                    {"exercise_id": exercise_ids[0], "order": 1, "target_sets": 3},
                    {"exercise_id": exercise_ids[1], "order": 2, "target_sets": 4},
                    {"exercise_id": exercise_ids[2], "order": 3, "target_sets": 3}
                ]
            }
        )
        assert response.status_code == 200
        assert len(response.json()["exercises"]) == 3

    def test_create_template_with_notes(self, client, sample_user):
        """Test creating template with exercise notes."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "With Notes",
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "notes": "Focus on form"
                    }
                ]
            }
        )
        assert response.status_code == 200
        assert response.json()["exercises"][0]["notes"] == "Focus on form"

    # Negative test cases
    def test_create_template_missing_name(self, client, sample_user):
        """Test creating template without name."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "exercises": [{"exercise_id": exercise_id, "order": 1}]
            }
        )
        assert response.status_code == 422

    def test_create_template_empty_name(self, client, sample_user):
        """Test creating template with empty name."""
        response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "",
                "exercises": []
            }
        )
        assert response.status_code == 422

    def test_get_nonexistent_template(self, client):
        """Test getting template that doesn't exist."""
        response = client.get("/api/templates/99999")
        assert response.status_code == 404

    def test_update_nonexistent_template(self, client):
        """Test updating template that doesn't exist."""
        response = client.put(
            "/api/templates/99999",
            json={
                "name": "New Name",
                "exercises": []
            }
        )
        assert response.status_code == 404

    def test_delete_nonexistent_template(self, client):
        """Test deleting template that doesn't exist."""
        response = client.delete("/api/templates/99999")
        assert response.status_code == 404

    def test_start_workout_nonexistent_template(self, client, sample_user):
        """Test starting workout from nonexistent template."""
        response = client.post(f"/api/templates/99999/start?user_id={sample_user['id']}")
        assert response.status_code == 404

    def test_create_template_missing_user_id(self, client):
        """Test creating template without user_id."""
        response = client.post(
            "/api/templates/",
            json={
                "name": "Test",
                "exercises": []
            }
        )
        assert response.status_code == 422

    def test_start_workout_missing_user_id(self, client, sample_user):
        """Test starting workout without user_id."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        create_response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Test",
                "exercises": [{"exercise_id": exercise_id, "order": 1}]
            }
        )
        template_id = create_response.json()["id"]

        response = client.post(f"/api/templates/{template_id}/start")
        assert response.status_code == 422

    def test_get_templates_empty_list(self, client, sample_user):
        """Test getting templates when none exist."""
        response = client.get(f"/api/templates/?user_id={sample_user['id']}")
        assert response.status_code == 200
        assert response.json() == []

    def test_template_exercise_invalid_order(self, client, sample_user):
        """Test template with duplicate exercise orders."""
        exercises_response = client.get("/api/exercises/")
        exercise_ids = [ex["id"] for ex in exercises_response.json()[:2]]

        # Duplicate orders should still work - just a logical issue
        response = client.post(
            f"/api/templates/?user_id={sample_user['id']}",
            json={
                "name": "Duplicate Orders",
                "exercises": [
                    {"exercise_id": exercise_ids[0], "order": 1},
                    {"exercise_id": exercise_ids[1], "order": 1}
                ]
            }
        )
        assert response.status_code == 200
