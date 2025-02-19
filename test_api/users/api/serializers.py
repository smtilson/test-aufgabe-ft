from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from ..models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_manager = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    # add owned stores and managed stores?
    # do I want to add this to the serializer?
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

    # This needs to validate that the password is sufficiently strong.
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
