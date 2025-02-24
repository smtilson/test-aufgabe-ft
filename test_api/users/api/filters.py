from django_filters.rest_framework import (
    FilterSet,
    NumberFilter,
    CharFilter,
    OrderingFilter,
)
from django.contrib.auth import get_user_model
from django.db.models import Q


class UserFilter(FilterSet):
    email = CharFilter(field_name="email")
    first_name = CharFilter(field_name="first_name")
    last_name = CharFilter(field_name="last_name")
    owned_stores = NumberFilter(field_name="owned_stores")
    managed_stores = NumberFilter(field_name="managed_stores")
    ordering = OrderingFilter(
        fields=(
            ("email", "email"),
            ("first_name", "first_name"),
            ("last_name", "last_name"),
        )
    )

    class Meta:
        model = get_user_model()
        fields = {
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "email": ["icontains"],
            "owned_stores": ["exact", "in"],
            "managed_stores": ["exact", "in"],
        }
