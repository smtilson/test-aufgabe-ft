from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    Group,
    Permission,
)
from rest_framework.authtoken.models import Token
from .managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # groups and user_permissions are explicit so that related_name can be set to prevent an error.
    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="customuser_set", blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def auth_token(self):
        token, _ = Token.objects.get_or_create(user=self)
        return token

    def __str__(self):
        return self.name + " (id: " + str(self.id) + ")"

    @property
    def is_owner(self):
        return self.owned_stores.count() > 0

    @property
    def is_manager(self):
        return self.managed_stores.count() > 0 or self.is_owner
