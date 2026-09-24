from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
            },
        }
    )


def test_get_activities_returns_activity_catalog():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant_to_activity():
    # Arrange
    reset_activities()
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup?email=" + email)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400_and_keeps_participants_unique():
    # Arrange
    reset_activities()
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup?email=" + email)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_unregister_removes_participant_from_activity():
    # Arrange
    reset_activities()
    email = "daniel@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/unregister?email=" + email)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_unknown_email_returns_404():
    # Arrange
    reset_activities()
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/unregister?email=" + email)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unknown_activity_returns_404_for_signup_and_unregister():
    # Arrange
    reset_activities()

    # Act
    signup_response = client.post("/activities/Unknown Club/signup?email=test@mergington.edu")
    unregister_response = client.delete("/activities/Unknown Club/unregister?email=test@mergington.edu")

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert unregister_response.status_code == 404
    assert unregister_response.json()["detail"] == "Activity not found"
