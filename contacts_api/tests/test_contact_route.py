import pytest
from fastapi.testclient import TestClient
from contacts_api.main import app
from contacts_api.services.auth import auth_service
import asyncio
client = TestClient(app)

@pytest.fixture
def access_token():
    user_data ={"sub":"testuser@example.com"}

    token = asyncio.run(auth_service.create_access_token(user_data))

    return f'Bearer {token}'

def test_create_contact(access_token):
    data = {
        "name": "John", 
        "email": "john@example.com", 
        "phone": "1234567890", 
        "birthday": None, 
        "about": "Test user"
    }
    headers = {"Authorization": access_token}
    response = client.post("/contacts/",json=data, headers=headers)
    assert response.status_code ==201
    result = response.json()
    assert result["name"] == "John"
    assert result['email'] == "john@example.com"

def test_get_contact(access_token):
    data = { "name": "Jane", 
            "email": "jane@example.com", 
            "phone": "9876543210", 
            "birthday": None, 
            "about": "Another test user" }
    headers = {"Authorization": access_token}
    response = client.post("/contacts/",json=data, headers=headers)
    created = response.json()
    contact_id = created["id"]

    response = client.get(f"/contacts/{contact_id}", headers=headers)
    assert response.status_code == 201
    result = response.json()
    assert result["id"]==contact_id
    assert result["name"]=="Jane"

    