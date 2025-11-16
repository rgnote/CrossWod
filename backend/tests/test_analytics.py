import pytest
from datetime import datetime, timezone, timedelta, date


class TestAnalyticsAPI:
    """Test analytics and progress tracking endpoints."""

    # Positive test cases
    def test_get_weekly_summary_no_workouts(self, client, sample_user):
        """Test weekly summary with no workouts."""
        response = client.get(f"/api/analytics/weekly-summary?user_id={sample_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_workouts"] == 0
        assert data["total_volume"] == 0
        assert data["total_sets"] == 0

    def test_get_weekly_summary_with_workouts(self, client, sample_user):
        """Test weekly summary with workout data."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        # Create workout today
        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 100}
                        ]
                    }
                ]
            }
        )

        response = client.get(f"/api/analytics/weekly-summary?user_id={sample_user['id']}")
        data = response.json()
        assert data["total_workouts"] == 1
        assert data["total_sets"] == 1
        assert data["total_volume"] == 1000
        assert "week_start" in data

    def test_get_weekly_summary_previous_week(self, client, sample_user):
        """Test getting previous week's summary."""
        response = client.get(f"/api/analytics/weekly-summary?user_id={sample_user['id']}&week_offset=1")
        assert response.status_code == 200
        data = response.json()
        assert data["total_workouts"] == 0

    def test_get_streak_info_no_workouts(self, client, sample_user):
        """Test streak info with no workouts."""
        response = client.get(f"/api/analytics/streak?user_id={sample_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["current_streak"] == 0
        assert data["longest_streak"] == 0
        assert data["total_workouts"] == 0
        assert data["last_workout_date"] is None

    def test_get_streak_info_with_workout(self, client, sample_user):
        """Test streak info after creating workout."""
        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": []
            }
        )

        response = client.get(f"/api/analytics/streak?user_id={sample_user['id']}")
        data = response.json()
        assert data["total_workouts"] == 1
        assert data["current_streak"] >= 0
        assert data["last_workout_date"] is not None

    def test_get_exercise_progress_no_data(self, client, sample_user):
        """Test exercise progress with no workout data."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.get(
            f"/api/analytics/exercise-progress?user_id={sample_user['id']}&exercise_id={exercise_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["dates"] == []
        assert data["values"] == []
        assert "exercise_name" in data

    def test_get_exercise_progress_with_data(self, client, sample_user):
        """Test exercise progress with workout data."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        # Create workout with weight progression
        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise_id,
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 100}
                        ]
                    }
                ]
            }
        )

        response = client.get(
            f"/api/analytics/exercise-progress?user_id={sample_user['id']}&exercise_id={exercise_id}"
        )
        data = response.json()
        assert len(data["dates"]) > 0
        assert len(data["values"]) > 0
        assert data["metric_type"] == "weight"

    def test_get_exercise_progress_volume_metric(self, client, sample_user):
        """Test exercise progress with volume metric."""
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
                            {"set_number": 1, "reps": 10, "weight": 50}
                        ]
                    }
                ]
            }
        )

        response = client.get(
            f"/api/analytics/exercise-progress?user_id={sample_user['id']}&exercise_id={exercise_id}&metric_type=volume"
        )
        data = response.json()
        assert data["metric_type"] == "volume"

    def test_get_body_weight_progress_no_data(self, client, sample_user):
        """Test body weight progress with no data."""
        response = client.get(f"/api/analytics/body-weight-progress?user_id={sample_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["dates"] == []
        assert data["weights"] == []

    def test_get_body_weight_progress_with_data(self, client, sample_user):
        """Test body weight progress with data."""
        # Add body metric
        client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={
                "date": date.today().isoformat(),
                "weight": 75.5
            }
        )

        response = client.get(f"/api/analytics/body-weight-progress?user_id={sample_user['id']}")
        data = response.json()
        assert len(data["dates"]) == 1
        assert data["weights"][0] == 75.5

    def test_get_muscle_group_balance_no_workouts(self, client, sample_user):
        """Test muscle group balance with no workouts."""
        response = client.get(f"/api/analytics/muscle-group-balance?user_id={sample_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["muscle_groups"] == {}

    def test_get_muscle_group_balance_with_workouts(self, client, sample_user):
        """Test muscle group balance with workout data."""
        exercises_response = client.get("/api/exercises/")
        exercise = exercises_response.json()[0]  # Bench Press: chest, triceps

        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": [
                    {
                        "exercise_id": exercise["id"],
                        "order": 1,
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 50},
                            {"set_number": 2, "reps": 10, "weight": 50}
                        ]
                    }
                ]
            }
        )

        response = client.get(f"/api/analytics/muscle-group-balance?user_id={sample_user['id']}")
        data = response.json()
        muscle_groups = data["muscle_groups"]
        # Should have sets counted for each muscle group
        assert len(muscle_groups) > 0

    def test_get_workout_frequency_no_workouts(self, client, sample_user):
        """Test workout frequency with no workouts."""
        response = client.get(f"/api/analytics/workout-frequency?user_id={sample_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["dates"] == {}

    def test_get_workout_frequency_with_workouts(self, client, sample_user):
        """Test workout frequency with workout data."""
        client.post(
            f"/api/workouts/?user_id={sample_user['id']}",
            json={
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exercises": []
            }
        )

        response = client.get(f"/api/analytics/workout-frequency?user_id={sample_user['id']}")
        data = response.json()
        assert len(data["dates"]) > 0
        today_str = date.today().isoformat()
        assert data["dates"].get(today_str, 0) >= 1

    def test_workout_frequency_custom_days(self, client, sample_user):
        """Test workout frequency with custom day range."""
        response = client.get(
            f"/api/analytics/workout-frequency?user_id={sample_user['id']}&days=90"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 90

    def test_muscle_group_balance_custom_days(self, client, sample_user):
        """Test muscle group balance with custom day range."""
        response = client.get(
            f"/api/analytics/muscle-group-balance?user_id={sample_user['id']}&days=60"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 60

    # Negative test cases
    def test_weekly_summary_invalid_week_offset(self, client, sample_user):
        """Test weekly summary with negative week offset."""
        response = client.get(
            f"/api/analytics/weekly-summary?user_id={sample_user['id']}&week_offset=-1"
        )
        assert response.status_code == 422

    def test_exercise_progress_invalid_metric_type(self, client, sample_user):
        """Test exercise progress with invalid metric type."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        response = client.get(
            f"/api/analytics/exercise-progress?user_id={sample_user['id']}&exercise_id={exercise_id}&metric_type=invalid"
        )
        assert response.status_code == 422

    def test_exercise_progress_days_out_of_range(self, client, sample_user):
        """Test exercise progress with days parameter out of range."""
        exercises_response = client.get("/api/exercises/")
        exercise_id = exercises_response.json()[0]["id"]

        # Days too small
        response = client.get(
            f"/api/analytics/exercise-progress?user_id={sample_user['id']}&exercise_id={exercise_id}&days=3"
        )
        assert response.status_code == 422

        # Days too large
        response = client.get(
            f"/api/analytics/exercise-progress?user_id={sample_user['id']}&exercise_id={exercise_id}&days=500"
        )
        assert response.status_code == 422

    def test_body_weight_progress_days_out_of_range(self, client, sample_user):
        """Test body weight progress with invalid days."""
        response = client.get(
            f"/api/analytics/body-weight-progress?user_id={sample_user['id']}&days=1"
        )
        assert response.status_code == 422

    def test_workout_frequency_days_out_of_range(self, client, sample_user):
        """Test workout frequency with invalid days."""
        response = client.get(
            f"/api/analytics/workout-frequency?user_id={sample_user['id']}&days=1000"
        )
        assert response.status_code == 422

    def test_muscle_balance_days_out_of_range(self, client, sample_user):
        """Test muscle group balance with invalid days."""
        response = client.get(
            f"/api/analytics/muscle-group-balance?user_id={sample_user['id']}&days=200"
        )
        assert response.status_code == 422

    def test_streak_nonexistent_user(self, client):
        """Test getting streak for nonexistent user."""
        response = client.get("/api/analytics/streak?user_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["total_workouts"] == 0

    def test_exercise_progress_nonexistent_exercise(self, client, sample_user):
        """Test progress for nonexistent exercise."""
        response = client.get(
            f"/api/analytics/exercise-progress?user_id={sample_user['id']}&exercise_id=99999"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["exercise_name"] == "Unknown"
        assert data["dates"] == []
