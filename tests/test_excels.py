# tests/test_excels.py

import json
import pytest
from tests.utils import get_auth_token
from digital_twin_migration.models.efficiency_app import Excel

@pytest.fixture
def auth_token():
    return get_auth_token()


def test_create_excel(client, app):
    """Test creating a new excel"""

    response = client.post(
        "/excels",
        headers={"Authorization": f"Bearer {auth_token()}"},
        json={
            "name": "Test Excel",
        },
    )
    
    assert response.status_code == 201
    
    # Assert data in the database
    with app.app_context():
        excel = Excel.query.filter_by(excel_filename="Test Excel").first()
        assert excel is not None
        assert excel.description == "This is a test excel"
        assert excel.user_id == "test_user"
    
    

def test_get_list_excels(client):
    """Test getting a list of excels"""

    response = client.get(
        "/excels",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    
def test_get_excel(client):
    """Test getting a specific excel"""

    ##Get excel_id
    response = client.get(
        "/excels",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.get_json()[0]
    excel_id = data["id"]
    
    response = client.get(
        f"/excels/{excel_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 200
    resp_data = response.get_json()
    assert resp_data["excel_filename"] == data["excel_filename"]
    
def test_update_excel(client):
    """Test updating a specific excel"""

    ##Get excel_id
    response = client.get(
        "/excels",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.get_json()[0]
    excel_id = data["id"]
    
    response = client.put(
        f"/excels/{excel_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Updated Excel",
        },
    )
    
    assert response.status_code == 200
    resp_data = response.get_json()
    assert resp_data["excel_filename"] == "Updated Excel"
    
def test_delete_excel(client):
    """Test deleting a specific excel"""

    ##Get excel_id
    response = client.get(
        "/excels",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.get_json()[0]
    excel_id = data["id"]
    
    response = client.delete(
        f"/excels/{excel_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 200
    
    response = client.get(
        f"/excels/{excel_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 404
    