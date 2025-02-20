from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from ..api.serializers import CustomUserSerializer, SignUpSerializer, LoginSerializer


class CustomUserSerializerTest(TestCase):
    def setUp(self):
        self.data = {
            "email": "test@example.com",
            "password": "secure_PASSWORD_123",
            "first_name": "John",
            "last_name": "Doe",
        }
        data1 = {key: value + "1" for key, value in self.data.items()}
        self.user = get_user_model().objects.create_user(**data1)

    def test_serialization(self):
        data = CustomUserSerializer(instance=self.user).data
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertNotIn("password", data)

    def test_deserialization(self):
        serializer = CustomUserSerializer(data=self.data)
        # check that the data is valid
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        # check user data
        self.assertEqual(user.email, self.data["email"])
        self.assertEqual(user.first_name, self.data["first_name"])
        self.assertEqual(user.last_name, self.data["last_name"])
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_read_only_fields(self):
        serializer = CustomUserSerializer(
            instance=self.user,
            data={
                "id": 8675309,
                "is_superuser": True,
                "is_staff": True,
                "is_active": False,
                "date_joined": "2025-01-01T00:00:00Z",
                "last_login": "2025-01-01T00:00:00Z",
            },
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        # check that the fields did not change
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertNotEqual(user.date_joined.isoformat(), "2025-01-01T00:00:00Z")
        self.assertIsNone(user.last_login)
        self.assertNotEqual(user.id, 8675309)

    def test_invalid_data(self):
        invalid_data = {"email": "not-an-email", "password": ""}
        serializer = CustomUserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)

    def test_create_method(self):
        serializer = CustomUserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertEqual(user.email, self.data["email"])
        #  check that the password is hashed
        self.assertTrue(user.check_password(self.data["password"]))
        self.assertNotEqual(user.password, self.data["password"])
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)


class SignUpSerializerTest(TestCase):
    def setUp(self):
        self.data = {
            "email": "test@example.com",
            "password": "secure_PASSWORD_123",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_valid_signup(self):
        serializer = SignUpSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertEqual(user.email, self.data["email"])
        self.assertTrue(
            user.check_password(self.data["password"])
        )  # Ensure password hashing
        self.assertEqual(user.first_name, self.data["first_name"])
        self.assertEqual(user.last_name, self.data["last_name"])
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_missing_fields(self):
        for _ in self.data.keys():
            data = {key: value for key, value in self.data.items() if key != _}
            serializer = SignUpSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(_, serializer.errors)

    def test_invalid_email(self):
        """Test that the serializer rejects an invalid email."""
        self.data["email"] = ("not-an-email",)
        serializer = SignUpSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_weak_password(self):
        self.data["password"] = "123"
        serializer = SignUpSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_duplicate_email(self):
        get_user_model().objects.create_user(**self.data)
        data = {key: value + "1" for key, value in self.data.items() if key != "email"}
        data["email"] = self.data["email"]
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class LoginSerializerTest(TestCase):
    def setUp(self):
        self.data = self.data = {
            "email": "test@example.com",
            "password": "secure_PASSWORD_123",
        }

        self.user = get_user_model().objects.create_user(**self.data)

    def test_valid_login(self):
        serializer = LoginSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_invalid_email(self):
        invalid_data = {"email": "wrong@example.com", "password": "secure_PASSWORD_123"}
        serializer = LoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        print()
        print(serializer.errors)
        ()
        self.assertEqual(
            serializer.errors["non_field_errors"][0], "Invalid email or password."
        )
        self.assertIsNone(serializer.validated_data.get("email"))

    def test_invalid_password(self):
        invalid_data = {"email": "test@example.com", "password": "wrongpassword"}
        serializer = LoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        print()
        print(serializer.errors)
        print()
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0], "Invalid email or password."
        )
        self.assertIsNone(serializer.validated_data.get("email"))

    def test_missing_fields(self):
        for _ in self.data.keys():
            missing_data = {key: value for key, value in self.data.items() if key != _}
            serializer = LoginSerializer(data=missing_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(_, serializer.errors)


# some of this seems like in belongs in testing views
# These should test each serializer
# testing serialization and deserialization
# see that password is hashed/handled correctly

# Test Signup serializer
## new user can be created
## that a token is created and returned
# Test Login serializer
## user can login
## token is returned
## user can't login with wrong password
## user can't login with wrong email
## bad credentials give a response
