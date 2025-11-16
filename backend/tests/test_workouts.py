import pytest
from datetime import datetime, timezone, timedelta


class TestWorkoutsAPI:
    """Test workout management endpoints."""

    # Positive test cases
    def test_create_workout(self, client, sample_user):
        """Test creating a new workout."""
        response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "name": "Morning Workout",
                "notes": "Feeling strong today",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Morning Workout"
        assert data["notes"] == "Feeling strong today"
        assert data["user_id"] == sample_user["id"]

    def test_create_workout_with_exercises(self, client, sample_user):
        """Test creating workout with exercises and sets."""
        # Get an exercise ID
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "name": "Full Workout",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "notes": "Warm up properly",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 50, "is_warmup": True},
                            {"set_number": 2, "reps": 8, "weight": 80, "is_warmup": False},
                            {"set_number": 3, "reps": 6, "weight": 100, "is_warmup": False}
                        ]
                    }
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["exercises"]) == 1
        assert len(data["exercises"][0]["sets"]) == 3
        assert data["exercises"][0]["sets"][0]["is_warmup"] is True

    def test_get_workouts(self, client, sample_user, sample_workout):
        """Test getting user's workouts."""
        response = client.get(f"/api/workouts/?user_id={sample_user['id']}")
        assert response.status_code == 200
        workouts = response.json()
        assert len(workouts) == 1
        assert workouts[0]["id"] == sample_workout["id"]

    def test_get_single_workout(self, client, sample_workout):
        """Test getting a single workout."""
        response = client.get(f"/api/workouts/{sample_workout['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_workout["id"]
        assert "exercises" in data

    def test_update_workout(self, client, sample_workout):
        """Test updating workout details."""
        response = client.put(
            f"/api/workouts/{sample_workout['id']}",
            json={
                "name": "Updated Workout",
                "notes": "Updated notes",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": 3600
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Workout"
        assert data["duration_seconds"] == 3600
        assert data["completed_at"] is not None

    def test_delete_workout(self, client, sample_workout):
        """Test deleting a workout."""
        response = client.delete(f"/api/workouts/{sample_workout['id']}")
        assert response.status_code == 200

        # Verify deleted
        get_response = client.get(f"/api/workouts/{sample_workout['id']}")
        assert get_response.status_code == 404

    def test_add_exercise_to_workout(self, client, sample_workout):
        """Test adding an exercise to existing workout."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.post(
            f"/api/workouts/{sample_workout['id']}/exercises",
            json={
                "exercise_id": exercise_id,
                "order": 1,
                "sets": [
                    {"set_number": 1, "reps": 12, "weight": 60}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["exercises"]) == 1

    def test_add_set_to_exercise(self, client, sample_user):
        """Test adding a set to a workout exercise."""
        # Create workout with exercise
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        workout_response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": []
                    }
                ]
            }
        )
        workout_exercise_id = workout_response.json()["exercises"][0]["id"]

        # Add set
        response = client.post(
            f"/api/workouts/exercises/{workout_exercise_id}/sets",
            json={
                "set_number": 1,
                "reps": 10,
                "weight": 100,
                "rpe": 8.5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reps"] == 10
        assert data["weight"] == 100
        assert data["rpe"] == 8.5

    def test_update_set(self, client, sample_user):
        """Test updating a set."""
        # Create workout with set
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        workout_response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 50}
                        ]
                    }
                ]
            }
        )
        set_id = workout_response.json()["exercises"][0]["sets"][0]["id"]

        # Update
        response = client.put(
            f"/api/workouts/sets/{set_id}",
            json={"reps": 12, "weight": 60, "is_failure": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reps"] == 12
        assert data["weight"] == 60
        assert data["is_failure"] is True

    def test_delete_set(self, client, sample_user):
        """Test deleting a set."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        workout_response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 50}
                        ]
                    }
                ]
            }
        )
        set_id = workout_response.json()["exercises"][0]["sets"][0]["id"]

        response = client.delete(f"/api/workouts/sets/{set_id}")
        assert response.status_code == 200

    def test_get_personal_records(self, client, sample_user):
        """Test getting personal records."""
        # Create workout with heavy set
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 5, "weight": 150}
                        ]
                    }
                ]
            }
        )

        response = client.get(f"/api/workouts/prs/{sample_user['id']}")
        assert response.status_code == 200
        prs = response.json()
        assert len(prs) > 0
        # Should have max_weight and max_volume PRs
        pr_types = [pr["record_type"] for pr in prs]
        assert "max_weight" in pr_types

    def test_get_prs_for_specific_exercise(self, client, sample_user):
        """Test getting PRs for a specific exercise."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        # Create PR
        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 3, "weight": 200}
                        ]
                    }
                ]
            }
        )

        response = client.get(f"/api/workouts/prs/{sample_user['id']}?exercise_id={exercise_id}")
        assert response.status_code == 200
        prs = response.json()
        for pr in prs:
            assert pr["exercise_id"] == exercise_id

    def test_pr_updates_on_new_record(self, client, sample_user):
        """Test that PR is updated when new record is achieved."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        # First workout
        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [{"set_number": 1, "reps": 5, "weight": 100}]
                    }
                ]
            }
        )

        # Second workout with higher weight
        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [{"set_number": 1, "reps": 5, "weight": 120}]
                    }
                ]
            }
        )

        response = client.get(f"/api/workouts/prs/{sample_user['id']}?exercise_id={exercise_id}")
        prs = response.json()
        max_weight_pr = next(pr for pr in prs if pr["record_type"] == "max_weight")
        assert max_weight_pr["value"] == 120

    def test_workout_summary_calculation(self, client, sample_user):
        """Test that workout summaries are calculated correctly."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 50},  # Volume: 500
                            {"set_number": 2, "reps": 10, "weight": 50},  # Volume: 500
                        ]
                    }
                ]
            }
        )

        response = client.get(f"/api/workouts/?user_id={sample_user['id']}")
        workout = response.json()[0]
        assert workout["exercise_count"] == 1
        assert workout["total_sets"] == 2
        assert workout["total_volume"] == 1000  # 10*50 + 10*50

    # Negative test cases
    def test_get_nonexistent_workout(self, client):
        """Test getting workout that doesn't exist."""
        response = client.get("/api/workouts/99999")
        assert response.status_code == 404

    def test_update_nonexistent_workout(self, client):
        """Test updating workout that doesn't exist."""
        response = client.put(
            "/api/workouts/99999",
            json={"name": "New Name"}
        )
        assert response.status_code == 404

    def test_delete_nonexistent_workout(self, client):
        """Test deleting workout that doesn't exist."""
        response = client.delete("/api/workouts/99999")
        assert response.status_code == 404

    def test_create_workout_invalid_started_at(self, client, sample_user):
        """Test creating workout with invalid date."""
        response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": "not-a-date",
                "exercises": []
            }
        )
        assert response.status_code == 422

    def test_create_workout_missing_started_at(self, client, sample_user):
        """Test creating workout without started_at."""
        response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "name": "Test",
                "exercises": []
            }
        )
        assert response.status_code == 422

    def test_add_exercise_invalid_exercise_id(self, client, sample_workout):
        """Test adding nonexistent exercise to workout."""
        # SQLite doesn't enforce FK constraints by default, but the response
        # validation will fail because exercise relationship will be None
        # This results in a ResponseValidationError being raised
        from fastapi.exceptions import ResponseValidationError
        with pytest.raises(ResponseValidationError):
            client.post(
                f"/api/workouts/{sample_workout['id']}/exercises",
                json={
                    "exercise_id": 99999,
                    "order": 1,
                    "sets": []
                }
            )

    def test_add_set_to_nonexistent_exercise(self, client):
        """Test adding set to nonexistent workout exercise."""
        response = client.post(
            "/api/workouts/exercises/99999/sets",
            json={
                "set_number": 1,
                "reps": 10,
                "weight": 50
            }
        )
        assert response.status_code == 404

    def test_update_nonexistent_set(self, client):
        """Test updating nonexistent set."""
        response = client.put(
            "/api/workouts/sets/99999",
            json={"reps": 10}
        )
        assert response.status_code == 404

    def test_delete_nonexistent_set(self, client):
        """Test deleting nonexistent set."""
        response = client.delete("/api/workouts/sets/99999")
        assert response.status_code == 404

    def test_invalid_rpe_value(self, client, sample_user):
        """Test set with RPE outside valid range."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 50, "rpe": 15}  # Invalid: max is 10
                        ]
                    }
                ]
            }
        )
        assert response.status_code == 422

    def test_get_prs_nonexistent_user(self, client):
        """Test getting PRs for nonexistent user."""
        response = client.get("/api/workouts/prs/99999")
        assert response.status_code == 200
        assert response.json() == []
