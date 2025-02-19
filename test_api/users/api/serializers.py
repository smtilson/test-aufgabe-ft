from rest_framework import serializers
from ..models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

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
            "is_manager",
            "is_owner",
            "is_staff",
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

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))
        return super().update(instance, validated_data)


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

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
