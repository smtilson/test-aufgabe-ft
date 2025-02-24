"""
Serializers for the CustomUser model and authentication-related functionality.

The `CustomUserSerializer` is used to serialize and deserialize the `CustomUser` model, including fields like `first_name`, `last_name`, `email`, `password`, and various flags like `is_manager`, `is_owner`, and `token`.

The `SignUpSerializer` is a specialized serializer for creating new `CustomUser` instances during the sign-up process, validating the password using the Django password validator.

The `LoginSerializer` is used to validate the email and password during the login process, and returns the authenticated user.
"""

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from ..models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_manager = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "date_joined",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_manager",
            "is_owner",
            "token",
        ]
        read_only_fields = [
            "id",
            "groups",
            "user_permissions",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
            "last_login",
        ]

    def get_token(self, obj):
        return obj.auth_token.key

    def get_is_manager(self, obj):
        return obj.is_manager

    def get_is_owner(self, obj):
        return obj.is_owner

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))
        return super().update(instance, validated_data)


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
        ]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                raise AuthenticationFailed("Invalid email or password.")
            data["user"] = user
        else:
            raise serializers.ValidationError("Both email and password are required.")
        return data
