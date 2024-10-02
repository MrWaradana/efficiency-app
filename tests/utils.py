import requests
from core.config import config


def get_auth_token():
    """Utility function to retrieve the auth token for testing."""
    response = requests.post(
        config.AUTH_SERVICE_API + "/sign-in",
        {
            "username": "Sue",
            "password": "password"
        }
    )
    

    return response.json()["data"]["access_token"]
