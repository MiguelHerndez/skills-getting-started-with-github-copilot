import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Helper to reset activities state for each test
def reset_activities():
    for activity in activities.values():
        activity["participants"] = []

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    reset_activities()
    yield
    reset_activities()

def test_get_activities():
    # Arrange
    # (No setup needed, activities are present)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_register_participant():
    # Arrange
    email = "test1@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert f"Signed up {email}" in response.json()["message"]

def test_prevent_duplicate_registration():
    # Arrange
    email = "test2@mergington.edu"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_participant():
    # Arrange
    email = "test3@mergington.edu"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})
    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    assert f"Removed {email}" in response.json()["message"]

def test_unregister_not_registered():
    # Arrange
    email = "notregistered@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_activity_not_found():
    # Arrange
    email = "test4@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
