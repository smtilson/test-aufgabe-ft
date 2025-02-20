from django.test import TestCase

# Create your tests here.


# test CRUD operations
# sample tests from gpt for views.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from ..models import CustomUser


class CustomUserViewSetTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="secure_PASSWORD_123",
            first_name="Test",
            last_name="User",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.url = reverse("customuser-list")

    def test_list_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_user(self):
        data = {
            "email": "newuser@example.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)

    def test_update_user(self):
        url = reverse("customuser-detail", args=[self.user.id])
        data = {"first_name": "Updated"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_delete_user(self):
        url = reverse("customuser-detail", args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CustomUser.objects.count(), 0)


class SignupViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("signup")

    def test_successful_signup(self):
        data = {
            "email": "signup@example.com",
            "password": "signup_password",
            "first_name": "Signup",
            "last_name": "User",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_signup_with_existing_email(self):
        CustomUser.objects.create_user(
            email="existing@example.com", password="password123"
        )
        data = {
            "email": "existing@example.com",
            "password": "signup_password",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="login@example.com", password="login_password"
        )
        self.url = reverse("login")

    def test_successful_login(self):
        data = {"email": "login@example.com", "password": "login_password"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_credentials(self):
        data = {"email": "login@example.com", "password": "wrong_password"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_login_missing_fields(self):
        data = {"email": "login@example.com"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
