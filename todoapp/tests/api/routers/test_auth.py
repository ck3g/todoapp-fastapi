from fastapi.testclient import TestClient
from fastapi import status
import pytest

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


@pytest.mark.parametrize(
    "email, password, password_confirmation, expected_type, expected_msg",
    [
        (
            "e",
            "pass123",
            "pass123",
            "string_too_short",
            "String should have at least 3 characters",
        ),
        (
            "email@example.com",
            "p",
            "p",
            "string_too_short",
            "String should have at least 3 characters",
        ),
        (
            "email@example.com",
            "pass123",
            "pass123456",
            "confirmation_error",
            "Password and Password Confirmation do not match",
        ),
    ],
    ids=[
        "email_string_too_short",
        "password_string_too_short",
        "password_and_confirmation_do_not_match",
    ],
)
def test_auth_register_validation_errors(
    email, password, password_confirmation, expected_type, expected_msg
):
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "password_confirmation": password_confirmation,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    for err in json_response["detail"]:
        assert expected_type == err["type"]
        assert expected_msg == err["msg"]
