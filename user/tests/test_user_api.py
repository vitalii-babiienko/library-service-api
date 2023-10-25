from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from user.serializers import UserSerializer

USER_CREATE_URL = reverse("user:create_user")
USER_MANAGE_URL = reverse("user:manage_user")


class UnauthenticatedUserApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user(self):
        payload = {
            "email": "test@email.com",
            "first_name": "Test First",
            "last_name": "Test Last",
            "password": "test_password",
        }
        res = self.client.post(USER_CREATE_URL, payload)
        user = get_user_model().objects.get(id=res.data["id"])

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "password":
                self.assertTrue(user.check_password(payload["password"]))
            else:
                self.assertEquals(payload[key], getattr(user, key))

    def test_manage_user_auth_required(self):
        res = self.client.get(USER_MANAGE_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@email.com",
            "test_password",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_user(self):
        res = self.client.get(USER_MANAGE_URL)

        serializer = UserSerializer(self.user)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_update_user(self):
        payload = {
            "email": "test@email.com",
            "first_name": "Test First UPD",
            "last_name": "Test Last UPD",
            "password": "test_password_upd",
        }
        res = self.client.put(USER_MANAGE_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        for key in payload:
            if key == "password":
                self.assertTrue(self.user.check_password(payload["password"]))
            else:
                self.assertEquals(payload[key], getattr(self.user, key))

        payload = {
            "first_name": "Test First Patched",
        }
        res = self.client.patch(USER_MANAGE_URL, payload)
        self.user.refresh_from_db()

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(payload["first_name"], self.user.first_name)
