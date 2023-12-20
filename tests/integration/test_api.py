import pytest
from fastapi.testclient import TestClient
from config_system.api import app

client = TestClient(app)

def test_get_config():
    response = client.get("/config/test")
    assert response.status_code == 200
