# User Views Tests

## Test CustomUserViewSet
### Test that a user can be created
### Test that a user can be updated
### Test that a user can be deleted
### Test that a user can be retrieved
### Test that a user can be listed
## SignupView
### Test that a user can be created
### Test that a token is created and returned
### test edge cases
## LoginView:
### Test login with valid credentials and ensure a token is returned.
### Test login with invalid credentials (e.g., wrong password or non-existent email).
### Test edge cases like empty or malformed requests.

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


User = get_user_model()


class CustomUserViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="secure_PASSWORD_123",
            first_name="John",
            last_name="Doe",
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        # check if this is the right way to set the token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.url = reverse("customuser-list")

    def test_list_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print()
        print(response.data)
        print()
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_user(self):
        data = {
            "email": "newuser@example.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

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
        self.assertEqual(User.objects.count(), 0)
