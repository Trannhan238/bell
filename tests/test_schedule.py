import pytest
from app import create_app, db
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_schedule(client):
    access_token = create_access_token(identity={"id": 1, "role": "admin"})
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "start_time": "08:00:00",
        "end_time": "09:00:00",
        "day_of_week": 1,
        "bell_type": "morning",
        "is_summer": False,
    }
    response = client.post("/api/schedule/create", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json["message"] == "Schedule created successfully"
