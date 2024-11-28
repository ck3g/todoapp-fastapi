from fastapi.testclient import TestClient
from starlette import status
from todoapp.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}
