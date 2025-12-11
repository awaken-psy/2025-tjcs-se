import requests

from .config import base_url
from .utils import get_admin_user
from .data import valid_emails, users
def test_register():
    codes = {}
    admin_user_info = get_admin_user()
    token = admin_user_info['token']

    for email in valid_emails:
        response = requests.post(f"{base_url}/auth/sendcode", json={"email": email})
        assert response.status_code == 200

    for email in valid_emails:
        response = requests.get(f"{base_url}/test/verification-code/{email}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        print(data)
        has_code = data['data']["has_code"]
        verification_code = data['data']["verification_code"]
        assert has_code
        codes[email] = verification_code

    for user in users:
        user["verify_code"] = codes[user["email"]]
        response = requests.post(f"{base_url}/auth/register", json=user)
        assert response.status_code == 200
        