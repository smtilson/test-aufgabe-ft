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
        day_fields = set(self.filters.keys())
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


class tempHoursFilter(FilterSet):
    opening_time = TimeFilter(lookup_expr="exact")
    opening_time_lte = TimeFilter(field_name="opening_time", lookup_expr="lte")

    class Meta:
        model = Store
        fields = ["opening_time"]


class HoursFilter(FilterSet, BaseFilterValidationMixin):
    opening_time = TimeFilter()
    opening_time_lte = TimeFilter(field_name="opening_time", lookup_expr="lte")
    # opening_time_gte = TimeFilter(field_name="opening_time", lookup_expr="gte")

    # closing_time = TimeFilter()
    # closing_time_lte = TimeFilter(field_name="closing_time", lookup_expr="lte")
    # closing_time_gte = TimeFilter(field_name="closing_time", lookup_expr="gte")

    ordering = OrderingFilter(
        fields=(
            ("opening_time", "opens"),
            ("closing_time", "closes"),
        )
    )

    class Meta:
        model = Store
        fields = {
            "opening_time": ["exact", "lte", "gte"],
            "closing_time": ["exact", "lte", "gte"],
        }
        fields = ["opening_time", "closing_time"]

    def filter_queryset(self, queryset):
        params = self.request.query_params
        print("\n\nfilter_queryset called on\n", params)
        # filter_kwargs = self._process_params_comparison(params)
        self.validate_filters(self.request.query_params)
        # queryset = queryset.filter(**filter_kwargs)
        return super().filter_queryset(queryset)

    def validate_filters(self, params):
        time_fields = set(self.filters.keys())
        allowed_params = time_fields | {"page", "page_size", "ordering"}

        self._validate_parameter_names(params, allowed_params)
        self._validate_time_fields(params, time_fields)

    def _validate_time_fields(self, params, time_fields):
        for field in time_fields:
            values = params.getlist(field)
            self._check_for_duplicates(field, values)
            self._validate_time_format(field, values)

    def _validate_time_format(self, field, values):
        print("validating time format", field, values)
        if values and not self._is_valid_time(values[0]):
            raise ValidationError(
                f"Invalid time format for {field}. Must be in HH:MM format (24-hour)"
            )
        elif values and self._is_valid_time(values[0]):
            print("valid time format")
            print(values[0])

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
