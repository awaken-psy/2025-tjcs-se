import pytest
import requests
import time

from .config import base_url
from .data import valid_emails
from .utils import get_admin_user

def test_get_verifycode():
    admin_user_data = get_admin_user()
    token = admin_user_data["token"]
    for email in valid_emails:
        response = requests.post(base_url + "/auth/sendcode", json={"email": email})
        assert response.status_code == 200

    for email in valid_emails:
        response = requests.get(base_url + f"/test/verification-code/{email}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    time.sleep(2)
        
