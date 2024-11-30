from fastapi.testclient import TestClient
from fastapi import status

from todoapp.main import app

client = TestClient(app)


def test_auth_register_successful_response():
    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "pwd123",
            "password_confirmation": "pwd123",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "msg": "User successfully created",
        "user": {"email": "user@example.com", "username": "user"},
    }
