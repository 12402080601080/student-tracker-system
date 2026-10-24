import pytest
from app import create_app
from app.extensions import get_db

@pytest.fixture
def app():
    app = create_app("testing")
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    # Log in as admin
    client.post("/auth/login", data={"username": "admin", "password": "Admin@123"}, follow_redirects=True)
    return client
