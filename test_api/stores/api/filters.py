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
from datetime import datetime
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


class BaseFilterValidationMixin:
    def _validate_parameter_names(self, params, allowed_params):
        invalid_params = set(params) - allowed_params
        if invalid_params:
            raise ValidationError(
                f"Invalid query parameter: {invalid_params.pop()}. Must be one of: {allowed_params}"
            )

    def _check_for_duplicates(self, field, values):
        if len(values) > 1:
            raise ValidationError(f"Duplicate query parameter found: {field}")

    def _add_pagination_params(self, allowed_params):
        return allowed_params | {"page", "page_size", "ordering"}


class DaysFilter(FilterSet, BaseFilterValidationMixin):
    montag = BooleanFilter()
    dienstag = BooleanFilter()
    mittwoch = BooleanFilter()
    donnerstag = BooleanFilter()
    freitag = BooleanFilter()
    samstag = BooleanFilter()
    sonntag = BooleanFilter()

    def filter_queryset(self, queryset):
        self.validate_filters(self.request.query_params)
        return super().filter_queryset(queryset)

    def validate_filters(self, params):
        params = self.request.query_params
        day_fields = {
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        }
        allowed_params = self._add_pagination_params(day_fields)

        self._validate_parameter_names(params, allowed_params)
        self._validate_day_fields(params, day_fields)

    def _validate_day_fields(self, params, day_fields):
        for field in day_fields:
            values = params.getlist(field)
            self._check_for_duplicates(field, values)
            self._validate_boolean_value(field, values)

    def _validate_boolean_value(self, field, values):
        if values and values[0].lower() not in {"true", "false"}:
            raise ValidationError(
                f"Invalid parameter, must be 'true' or 'false': {field}"
            )


class HoursFilter(FilterSet, BaseFilterValidationMixin):
    opening_time = TimeFilter(lookup_expr="exact|lt|lte|gt|gte")
    closing_time = TimeFilter(lookup_expr="exact|lt|lte|gt|gte")
    ordering = OrderingFilter(
        fields=(
            ("opening_time", "opens"),
            ("closing_time", "closes"),
        )
    )

    def filter_queryset(self, queryset):
        self.validate_filters(self.request.query_params)
        return super().filter_queryset(queryset)

    def validate_filters(self, params):
        time_fields = {"opening_time", "closing_time"}
        allowed_params = time_fields | {"page", "page_size", "ordering"}

        self._validate_parameter_names(params, allowed_params)
        self._validate_time_fields(params, time_fields)

    def _validate_time_fields(self, params, time_fields):
        for field in time_fields:
            values = params.getlist(field)
            self._check_for_duplicates(field, values)
            self._validate_time_format(field, values)

    def _validate_time_format(self, field, values):
        if values and not self._is_valid_time(values[0]):
            raise ValidationError(
                f"Invalid time format for {field}. Must be in HH:MM format (24-hour)"
            )

    def _is_valid_time(self, time_str):
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False


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
