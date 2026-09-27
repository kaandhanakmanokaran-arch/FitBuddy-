def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_generate_and_feedback(client):
    payload = {
        "username": "Demo User",
        "user_id": "demo-1",
        "age": 25,
        "weight": 65,
        "goal": "general wellness",
        "intensity": "medium",
    }
    response = client.post("/api/workout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "demo-1"
    assert "Day 1" in data["workout_plan"]

    feedback = client.post(
        "/api/feedback",
        json={"user_id": "demo-1", "feedback": "Add more mobility and one full rest day."},
    )
    assert feedback.status_code == 200
    assert "Feedback applied" in feedback.json()["updated_plan"]
