from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from ..api.serializers import CustomUserSerializer, SignUpSerializer, LoginSerializer


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print(f"\nInitializing test class: {cls.__name__}")


class CustomUserSerializerTest(BaseTestCase):
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
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

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

        self.assertTrue(user.check_password(self.data["password"]))
        self.assertNotEqual(user.password, self.data["password"])
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)


class SignUpSerializerTest(BaseTestCase):
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


class LoginSerializerTest(BaseTestCase):
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
        with self.assertRaises(AuthenticationFailed) as e:
            serializer.is_valid()
        self.assertEqual(str(e.exception), "Invalid email or password.")
        self.assertEqual(e.exception.status_code, 401)
        self.assertEqual(e.exception.detail.code, "authentication_failed")

    def test_invalid_password(self):
        invalid_data = {"email": "test@example.com", "password": "wrongpassword"}
        serializer = LoginSerializer(data=invalid_data)
        with self.assertRaises(AuthenticationFailed) as e:
            serializer.is_valid()
        self.assertEqual(str(e.exception), "Invalid email or password.")
        self.assertEqual(e.exception.status_code, 401)
        self.assertEqual(e.exception.detail.code, "authentication_failed")

    def test_missing_fields(self):
        for _ in self.data.keys():
            missing_data = {key: value for key, value in self.data.items() if key != _}
            serializer = LoginSerializer(data=missing_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(_, serializer.errors)
