import pytest
import requests

from .config import admin_user_email, admin_user_name, admin_user_password, base_url
from .data import valid_emails, users

def get_admin_user():
    data = requests.request("POST", url = base_url + "/auth/login", json = {
        "email" : admin_user_email,
        "password" : admin_user_password
    }).json()
    # print(data)
    assert data["code"] == 200
    return {
        "user_id": data["data"]["user_id"],
        "token": data["data"]["token"]
    }

def get_registered_users():
    user_info = []
    for user in users:
        response = requests.request("POST", url=base_url+"/auth/login", json={
            "email": user["email"],
            "password": user["password"]    
        })
        assert response.status_code == 200
        data = response.json()["data"]
        user["token"] = data["token"]
    return users
