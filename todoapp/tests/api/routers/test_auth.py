from fastapi.testclient import TestClient
from fastapi import status

from todoapp.main import app

client = TestClient(app)


def test_auth_register_successful_response():
    response = client.post("/auth/register")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"msg": "User successfully created"}
