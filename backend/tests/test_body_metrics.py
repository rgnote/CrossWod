import pytest
from datetime import date
from io import BytesIO


class TestBodyMetricsAPI:
    """Test body metrics and progress photos endpoints."""

    # Positive test cases
    def test_create_body_metric(self, client, sample_user):
        """Test creating a body metric entry."""
        response = client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={
                "date": date.today().isoformat(),
                "weight": 75.5,
                "body_fat_percentage": 15.0,
                "notes": "Morning weight"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["weight"] == 75.5
        assert data["body_fat_percentage"] == 15.0
        assert data["user_id"] == sample_user["id"]

    def test_create_body_metric_with_measurements(self, client, sample_user):
        """Test creating body metric with measurements."""
        response = client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={
                "date": date.today().isoformat(),
                "weight": 80.0,
                "measurements": {
                    "chest": 100,
                    "waist": 85,
                    "arms": 38,
                    "thighs": 60
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["measurements"]["chest"] == 100
        assert data["measurements"]["waist"] == 85

    def test_get_body_metrics(self, client, sample_user):
        """Test getting body metrics list."""
        # Create a metric
        client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={
                "date": date.today().isoformat(),
                "weight": 70.0
            }
        )

        response = client.get(f"/api/body-metrics/?user_id={sample_user['id']}")
        assert response.status_code == 200
        metrics = response.json()
        assert len(metrics) == 1
        assert metrics[0]["weight"] == 70.0

    def test_update_existing_metric_same_date(self, client, sample_user):
        """Test that creating metric on same date updates it."""
        today = date.today().isoformat()

        # First creation
        client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={"date": today, "weight": 70.0}
        )

        # Second creation on same date should update
        response = client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={"date": today, "weight": 71.0}
        )
        assert response.status_code == 200
        assert response.json()["weight"] == 71.0

        # Should still only have one metric
        metrics = client.get(f"/api/body-metrics/?user_id={sample_user['id']}")
        assert len(metrics.json()) == 1

    def test_delete_body_metric(self, client, sample_user):
        """Test deleting a body metric."""
        create_response = client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={"date": date.today().isoformat(), "weight": 75.0}
        )
        metric_id = create_response.json()["id"]

        response = client.delete(f"/api/body-metrics/{metric_id}")
        assert response.status_code == 200

        # Verify deleted
        metrics = client.get(f"/api/body-metrics/?user_id={sample_user['id']}")
        assert len(metrics.json()) == 0

    def test_get_body_metrics_with_limit(self, client, sample_user):
        """Test getting body metrics with custom limit."""
        response = client.get(f"/api/body-metrics/?user_id={sample_user['id']}&limit=10")
        assert response.status_code == 200

    def test_upload_progress_photo(self, client, sample_user):
        """Test uploading a progress photo."""
        from PIL import Image
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        response = client.post(
            f"/api/body-metrics/photos?user_id={sample_user['id']}&photo_date={date.today().isoformat()}&category=front",
            files={"file": ("progress.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "front"
        assert data["user_id"] == sample_user["id"]

    def test_get_progress_photos(self, client, sample_user):
        """Test getting progress photos list."""
        # Upload a photo first
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        client.post(
            f"/api/body-metrics/photos?user_id={sample_user['id']}&photo_date={date.today().isoformat()}",
            files={"file": ("test.png", img_bytes, "image/png")}
        )

        response = client.get(f"/api/body-metrics/photos?user_id={sample_user['id']}")
        assert response.status_code == 200
        photos = response.json()
        assert len(photos) == 1

    def test_get_progress_photo_image(self, client, sample_user):
        """Test retrieving actual photo data."""
        from PIL import Image
        img = Image.new('RGB', (150, 150), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        create_response = client.post(
            f"/api/body-metrics/photos?user_id={sample_user['id']}&photo_date={date.today().isoformat()}",
            files={"file": ("photo.jpg", img_bytes, "image/jpeg")}
        )
        photo_id = create_response.json()["id"]

        response = client.get(f"/api/body-metrics/photos/{photo_id}/image")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

    def test_delete_progress_photo(self, client, sample_user):
        """Test deleting a progress photo."""
        from PIL import Image
        img = Image.new('RGB', (50, 50), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        create_response = client.post(
            f"/api/body-metrics/photos?user_id={sample_user['id']}&photo_date={date.today().isoformat()}",
            files={"file": ("photo.png", img_bytes, "image/png")}
        )
        photo_id = create_response.json()["id"]

        response = client.delete(f"/api/body-metrics/photos/{photo_id}")
        assert response.status_code == 200

        # Verify deleted
        photos = client.get(f"/api/body-metrics/photos?user_id={sample_user['id']}")
        assert len(photos.json()) == 0

    def test_progress_photo_with_notes(self, client, sample_user):
        """Test uploading progress photo with notes."""
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='purple')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        response = client.post(
            f"/api/body-metrics/photos?user_id={sample_user['id']}&photo_date={date.today().isoformat()}&notes=After%20workout",
            files={"file": ("photo.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 200
        assert response.json()["notes"] == "After workout"

    # Negative test cases
    def test_create_body_metric_missing_date(self, client, sample_user):
        """Test creating metric without date."""
        response = client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={"weight": 75.0}
        )
        assert response.status_code == 422

    def test_create_body_metric_invalid_date(self, client, sample_user):
        """Test creating metric with invalid date format."""
        response = client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={"date": "not-a-date", "weight": 75.0}
        )
        assert response.status_code == 422

    def test_delete_nonexistent_metric(self, client):
        """Test deleting metric that doesn't exist."""
        response = client.delete("/api/body-metrics/99999")
        assert response.status_code == 404

    def test_upload_non_image_as_progress_photo(self, client, sample_user):
        """Test uploading non-image file as progress photo."""
        text_file = BytesIO(b"This is text, not an image")
        response = client.post(
            f"/api/body-metrics/photos?user_id={sample_user['id']}&photo_date={date.today().isoformat()}",
            files={"file": ("text.txt", text_file, "text/plain")}
        )
        assert response.status_code == 400

    def test_get_nonexistent_photo_image(self, client):
        """Test getting image for nonexistent photo."""
        response = client.get("/api/body-metrics/photos/99999/image")
        assert response.status_code == 404

    def test_delete_nonexistent_photo(self, client):
        """Test deleting nonexistent photo."""
        response = client.delete("/api/body-metrics/photos/99999")
        assert response.status_code == 404

    def test_upload_photo_missing_date(self, client, sample_user):
        """Test uploading photo without date parameter."""
        from PIL import Image
        img = Image.new('RGB', (50, 50), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        response = client.post(
            f"/api/body-metrics/photos?user_id={sample_user['id']}",
            files={"file": ("photo.png", img_bytes, "image/png")}
        )
        assert response.status_code == 422

    def test_get_metrics_limit_out_of_range(self, client, sample_user):
        """Test getting metrics with limit out of range."""
        response = client.get(f"/api/body-metrics/?user_id={sample_user['id']}&limit=1000")
        assert response.status_code == 422

    def test_get_photos_limit_out_of_range(self, client, sample_user):
        """Test getting photos with limit out of range."""
        response = client.get(f"/api/body-metrics/photos?user_id={sample_user['id']}&limit=200")
        assert response.status_code == 422

    def test_body_metric_partial_data(self, client, sample_user):
        """Test creating metric with only weight (no other fields)."""
        response = client.post(
            f"/api/body-metrics/?user_id={sample_user['id']}",
            json={
                "date": date.today().isoformat(),
                "weight": 80.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["weight"] == 80.0
        assert data["body_fat_percentage"] is None
        assert data["measurements"] is None
