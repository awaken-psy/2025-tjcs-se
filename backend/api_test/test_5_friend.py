import requests
import pytest
from datetime import datetime, timedelta
import uuid

from .config import base_url
from .utils import get_admin_user, get_registered_users

class TestFriend:
    @pytest.fixture(scope="class")
    def get_users(self):
        return get_registered_users()

    def test_add_friend(self):
        admin_user = get_admin_user()
        users = get_registered_users()