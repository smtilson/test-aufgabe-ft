from django.core.validators import MinValueValidator
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
from .serializers import (
    StoreSerializer,
    DaysSerializer,
    HoursSerializer,
    ManagersSerializer,
)


class BaseFilterValidationMixin:
    def _validate_parameter_names(self, params, allowed_params):
        invalid_params = set(params) - allowed_params
        if invalid_params:
            raise ValidationError(
                f"Invalid query parameter: {invalid_params.pop()}. Must be one of: {allowed_params}"
            )

    def _add_default_params(self, allowed_params):
        return allowed_params | {"page", "page_size", "ordering"}

    def _reject_all_empty(self, params):
        for field in params.keys():
            values = params.getlist(field)
            self._reject_empty_values(field, values)

    def _reject_empty_values(self, field, values):
        if not values:
            raise ValidationError(f"Empty values not allowed for {field}")
        for value in values:
            if not value:
                raise ValidationError(f"Empty values not allowed for {field}")

    # Originally from Manager Filter
    def _validate_name(self, name):
        if not any(char.isalpha() for char in name):
            raise ValidationError("Name must contain at least one letter")

    # Originally from Days Filter
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

    def _check_for_duplicate(self, field, values):
        if len(values) > 1:
            raise ValidationError(f"Duplicate query parameter found: {field}")

    def _check_for_duplicates(self, params):
        for field in params.keys():
            values = params.getlist(field)
            self._check_for_duplicate(field, values)

    def _base_validation(self, params, allowed_params):
        self._reject_all_empty(params)
        self._validate_parameter_names(params, allowed_params)
        self._check_for_duplicates(params)

    @property
    def _extra_allowed_params(self):
        return {"page", "page_size", "ordering"}


class DaysFilter(FilterSet, BaseFilterValidationMixin):
    montag = BooleanFilter()
    dienstag = BooleanFilter()
    mittwoch = BooleanFilter()
    donnerstag = BooleanFilter()
    freitag = BooleanFilter()
    samstag = BooleanFilter()
    sonntag = BooleanFilter()

    def filter_queryset(self, queryset):
        params = self.request.query_params
        if self.request.method == "GET":
            non_page_params = {
                k for k in params.keys() if k not in {"page", "page_size"}
            }
            if non_page_params:
                self.validate_filters(params)
        return super().filter_queryset(queryset)

    def validate_filters(self, params):
        params = self.request.query_params
        day_fields = set(self.filters.keys())
        allowed_params = self._add_default_params(day_fields)
        self._base_validation(params, allowed_params)


class HoursFilter(FilterSet, BaseFilterValidationMixin):
    opening_time = TimeFilter()
    opening_time_lte = TimeFilter(field_name="opening_time", lookup_expr="lte")
    opening_time_gte = TimeFilter(field_name="opening_time", lookup_expr="gte")

    closing_time = TimeFilter()
    closing_time_lte = TimeFilter(field_name="closing_time", lookup_expr="lte")
    closing_time_gte = TimeFilter(field_name="closing_time", lookup_expr="gte")

    ordering = OrderingFilter(
        fields=(
            ("opening_time", "opens"),
            ("closing_time", "closes"),
        )
    )

    class Meta:
        model = Store
        fields = ["opening_time", "closing_time"]

    def filter_queryset(self, queryset):
        params = self.request.query_params
        if self.request.method == "GET":
            non_page_params = {
                k for k in params.keys() if k not in {"page", "page_size"}
            }
            if non_page_params:
                self.validate_filters(params)
        return super().filter_queryset(queryset)

    def validate_filters(self, params):
        time_fields = set(self.filters.keys())
        allowed_params = time_fields | {"page", "page_size", "ordering"}
        self._base_validation(params, allowed_params)


class ManagersFilter(FilterSet, BaseFilterValidationMixin):
    manager_ids = NumberFilter(
        lookup_expr="exact",
        validators=[MinValueValidator(1, message="Invalid manager ID")],
    )
    manager_ids_in = NumberFilter(
        lookup_expr="in",
        validators=[MinValueValidator(1, message="Invalid manager ID")],
    )
    manager_first_name = CharFilter(
        field_name="manager_ids__first_name", lookup_expr="icontains"
    )
    manager_last_name = CharFilter(
        field_name="manager_ids__last_name", lookup_expr="icontains"
    )
    ordering = OrderingFilter(
        fields=(
            ("manager_ids__first_name", "first_name"),
            ("manager_ids__last_name", "last_name"),
        )
    )

    class Meta:
        model = Store
        fields = ["manager_ids"]

    def filter_queryset(self, queryset):
        params = self.request.query_params
        if self.request.method == "GET":
            non_page_params = {
                k for k in params.keys() if k not in {"page", "page_size"}
            }
            if non_page_params:
                self.validate_filters(params)
        return super().filter_queryset(queryset)

    def validate_filters(self, params):
        manager_fields = set(self.filters.keys())
        allowed_params = self._add_default_params(manager_fields)
        self._base_validation(params, allowed_params)
        for field in set(params.keys()):
            values = params.getlist(field)
            # Validate names only for name-related fields
            if "name" in field:
                self._validate_name(values[0])


class StoreFilter(FilterSet, BaseFilterValidationMixin):
    # Define all store-specific filters
    name = CharFilter(lookup_expr="icontains")
    city = CharFilter(lookup_expr="icontains")
    address = CharFilter(lookup_expr="icontains")
    state_choices = [(k, k + ": " + v) for k, v in Store.STATES.items()]
    state_choices.sort(key=lambda x: x[0])
    state_abbrv = ChoiceFilter(choices=state_choices, lookup_expr="icontains")
    plz = CharFilter(lookup_expr="exact")

    owner_ids = NumberFilter(
        lookup_expr="exact",
        validators=[MinValueValidator(1, message="Invalid owner ID")],
    )
    owner_ids_in = NumberFilter(
        lookup_expr="in",
        validators=[MinValueValidator(1, message="Invalid owner ID")],
    )
    owner_first_name = CharFilter(
        field_name="owner_ids__first_name", lookup_expr="icontains"
    )
    owner_last_name = CharFilter(
        field_name="owner_ids__last_name", lookup_expr="icontains"
    )

    # From ManagersFilter
    manager_ids = NumberFilter(
        lookup_expr="exact",
        validators=[MinValueValidator(1, message="Invalid manager ID")],
    )
    manager_ids_in = NumberFilter(
        lookup_expr="in",
        validators=[MinValueValidator(1, message="Invalid manager ID")],
    )
    manager_first_name = CharFilter(
        field_name="manager_ids__first_name", lookup_expr="icontains"
    )
    manager_last_name = CharFilter(
        field_name="manager_ids__last_name", lookup_expr="icontains"
    )

    # From HoursFilter
    opening_time = TimeFilter()
    opening_time_lte = TimeFilter(field_name="opening_time", lookup_expr="lte")
    opening_time_gte = TimeFilter(field_name="opening_time", lookup_expr="gte")
    closing_time = TimeFilter()
    closing_time_lte = TimeFilter(field_name="closing_time", lookup_expr="lte")
    closing_time_gte = TimeFilter(field_name="closing_time", lookup_expr="gte")

    # From DaysFilter
    montag = BooleanFilter()
    dienstag = BooleanFilter()
    mittwoch = BooleanFilter()
    donnerstag = BooleanFilter()
    freitag = BooleanFilter()
    samstag = BooleanFilter()
    sonntag = BooleanFilter()

    # From ManagersFilter
    manager_ids = NumberFilter(lookup_expr="exact")
    manager_ids_in = NumberFilter(field_name="manager_ids", lookup_expr="in")
    manager_first_name = CharFilter(
        field_name="manager_ids__first_name", lookup_expr="icontains"
    )
    manager_last_name = CharFilter(
        field_name="manager_ids__last_name", lookup_expr="icontains"
    )

    ordering = OrderingFilter(
        fields=(
            ("name", "name"),
            ("city", "city"),
            ("state_abbrv", "state"),
            ("opening_time", "opens"),
            ("closing_time", "closes"),
        )
    )

    class Meta:
        model = Store
        fields = "__all__"

    def filter_queryset(self, queryset):
        params = self.request.query_params
        print(f"\nIncoming params: {params}")
        print(f"\nAvailable filtersms: {self.filters.keys()}")
        if self.request.method == "GET":
            non_page_params = {
                k for k in params.keys() if k not in {"page", "page_size"}
            }
            print(f"Non-page parameters: {non_page_params}")

            if non_page_params:
                self.validate_filters(params)
        return super().filter_queryset(queryset)

    # maybe refactor most of this into a base class method

    def validate_filters(self, params):
        allowed_params = self.filters.keys()
        allowed_params = self._add_default_params(self.filters.keys())
        print(allowed_params)
        self._base_validation(params, allowed_params)
        serializer_params = {
            k: v for k, v in params.items() if k not in self._extra_allowed_params
        }
        print("\nabout to serialize\n")
        print(f"\n{serializer_params}\n")
        serializer = StoreSerializer(
            data=serializer_params, context={"request": self.request}
        )

        valid = serializer.is_valid(raise_exception=True)
        print("\nserialized\n")
        if not valid:
            print("\nserializer is not valid\n")
            print(f"\nSerializer errors: {serializer.errors}\n")
