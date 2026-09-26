from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_home_has_planner_form():

    response = client.get("/")

    assert response.status_code == 200

    assert "Generate My Plan" in response.text

    assert "name=\"user_id\"" in response.text


def test_generate_demo():

    response = client.post(

        "/api/generate",

        json={

            "username": "Test User",

            "user_id": "test-001",

            "age": 20,

            "weight": 65,

            "goal": "General Wellness",

            "intensity": "medium"
        }
    )


    assert response.status_code == 200


    data = response.json()


    assert data["user_id"] == "test-001"


    assert "Day 1" in data["workout_plan"]