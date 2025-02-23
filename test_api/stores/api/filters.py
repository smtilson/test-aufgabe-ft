from django_filters.rest_framework import (
    FilterSet,
    NumberFilter,
    CharFilter,
    OrderingFilter,
    BooleanFilter,
    ChoiceFilter,
    TimeFilter,
)
from rest_framework.exceptions import ValidationError
from ..models import Store


class StoreFilter(FilterSet):
    name = CharFilter(lookup_expr="icontains")
    city = CharFilter(lookup_expr="icontains")
    address = CharFilter(lookup_expr="icontains")
    state_choices = [(k, k + ": " + v) for k, v in Store.STATES.items()]

    state_choices.sort(key=lambda x: x[0])
    state_abbrv = ChoiceFilter(choices=state_choices, lookup_expr="icontains")
    plz = CharFilter(lookup_expr="exact")
    owner_id = NumberFilter(lookup_expr="exact")
    owner_first_name = CharFilter(
        field_name="owner_id__first_name", lookup_expr="icontains"
    )
    owner_last_name = CharFilter(
        field_name="owner_id__last_name", lookup_expr="icontains"
    )
    manager_ids = NumberFilter(lookup_expr=["exact", "in"])
    manager_first_name = CharFilter(
        field_name="manager_ids__first_name", lookup_expr="icontains"
    )
    manager_last_name = CharFilter(
        field_name="manager_ids__last_name", lookup_expr="icontains"
    )
    opening_time = TimeFilter(lookup_expr=["exact", "lt", "gt"])
    closing_time = TimeFilter(lookup_expr=["exact", "lt", "gt"])

    # Days filters
    montag = BooleanFilter()
    dienstag = BooleanFilter()
    mittwoch = BooleanFilter()
    donnerstag = BooleanFilter()
    freitag = BooleanFilter()
    samstag = BooleanFilter()
    sonntag = BooleanFilter()

    ordering = OrderingFilter(
        fields=(
            ("name", "name"),
            ("city", "city"),
            ("state_abbrv", "state"),
            ("plz", "plz"),
            ("created_at", "created"),
            ("updated_at", "updated"),
            ("opening_time", "opens"),
            ("closing_time", "closes"),
        )
    )


class DaysFilter(FilterSet):
    montag = BooleanFilter()
    dienstag = BooleanFilter()
    mittwoch = BooleanFilter()
    donnerstag = BooleanFilter()
    freitag = BooleanFilter()
    samstag = BooleanFilter()
    sonntag = BooleanFilter()

    def filter_queryset(self, queryset):
        params = self.request.query_params
        day_fields = [
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        ]
        allowed_params = {
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
            "page",
            "page_size",
        }
        # Check for duplicates
        for param in params:
            if param not in allowed_params:
                raise ValidationError(
                    f"Invalid query parameter: {param}. Must be one of: {day_fields}"
                )
        for field in day_fields:
            values = params.getlist(field)
            if len(params.getlist(field)) > 1:
                raise ValidationError(f"Duplicate query parameter found: {field}")
            if values:
                if values[0].lower() not in {"true", "false"}:
                    raise ValidationError(
                        f"Invalid parameter, must be 'true' or 'false': {field}"
                    )
        return super().filter_queryset(queryset)


class HoursFilter(FilterSet):
    opening_time = TimeFilter(lookup_expr=["exact", "lt", "gt"])
    closing_time = TimeFilter(lookup_expr=["exact", "lt", "gt"])
    ordering = OrderingFilter(
        fields=(
            ("opening_time", "opens"),
            ("closing_time", "closes"),
        )
    )


class ManagersFilter(FilterSet):
    manager_ids = NumberFilter(lookup_expr=["exact", "in"])
    manager_first_name = CharFilter(
        field_name="manager_ids__first_name", lookup_expr="icontains"
    )
    manager_last_name = CharFilter(
        field_name="manager_ids__last_name", lookup_expr="icontains"
    )
    ordering = OrderingFilter(
        fields=(
            ("manager_first_name", "first_name"),
            ("manager_last_name", "last_name"),
        )
    )
