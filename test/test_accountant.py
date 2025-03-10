from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_accountant():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}