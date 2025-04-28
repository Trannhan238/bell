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

def test_register_device(client):
    data = {
        "mac_address": "00:1A:2B:3C:4D:5B",
        "school_id": 1
    }
    response = client.post("/api/device/register", json=data)
    assert response.status_code == 201
    assert response.json["message"] == "Device registered successfully"

def test_authenticate_device(client):
    data = {
        "mac_address": "00:1A:2B:3C:4D:5B"
    }
    response = client.post("/api/device/authenticate", json=data)
    assert response.status_code == 200
    assert "token" in response.json