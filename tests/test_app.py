import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activity_data(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays at 3:30 PM",
            "max_participants": 12,
            "participants": ["student@example.com"],
        },
        "Art Club": {
            "description": "Explore visual arts",
            "schedule": "Mondays at 3:30 PM",
            "max_participants": 15,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app, follow_redirects=False) as test_client:
        yield test_client


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client, activity_data):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activity_data


def test_signup_adds_participant(client, activity_data):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }
    assert email in activity_data["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Student is already signed up for this activity"
    )


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post(
        "/activities/Unknown%20Activity/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email(client):
    # Arrange

    # Act
    response = client.post("/activities/Chess%20Club/signup")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]