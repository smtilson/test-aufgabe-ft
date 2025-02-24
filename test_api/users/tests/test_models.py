from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.db import IntegrityError


# Model Tests
# these chould test creation of users and token association at creation.

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print(f"\nInitializing test class: {cls.__name__}")


class CustomUserModelTest(BaseTestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            # is this password sufficient?
            "password": "secure_PASSWORD_123",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        # correct data
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertEqual(user.last_name, self.user_data["last_name"])

        # token associated with the user
        self.assertIsNotNone(user.auth_token)
        # does the auth token have this?
        self.assertEqual(user.auth_token.user, user)

        # user properties
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_owner)
        self.assertFalse(user.is_manager)

    def test_user_str(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.name, f"{user.first_name} {user.last_name}")
        self.assertEqual(str(user), user.name + " (id: " + str(user.id) + ")")

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(**self.user_data)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)

    def test_token_on_creation(self):
        user = User.objects.create_user(**self.user_data)
        token = Token.objects.get(user=user)
        self.assertEqual(token.user, user)
        # tests user.auth_token method works properly
        self.assertEqual(token.key, user.auth_token.key)

    def test_email_uniqueness(self):
        dummy_data = {"email": "test@example.com", "password": "testpassword"}
        User.objects.create_user(**dummy_data)
        dummy_data["password"] += "1234"
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**dummy_data)
