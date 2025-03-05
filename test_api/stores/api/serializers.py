from rest_framework import serializers
from ..models import Store, DAYS_OF_WEEK, StoreHours
from users.models import CustomUser


class BaseSerializerMixin:
    # Check format methods
    # Checks if field names are valid
    def _check_unknown_fields(self, data):
        # Get the known fields from the serializer
        known_fields = set(self.fields.keys())
        # Get the incoming fields from the data
        incoming_fields = set(data.keys())

        # Find any unknown fields
        unknown_fields = incoming_fields - known_fields
        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not recognized." for field in unknown_fields}
            )

    # Check if hour values are valid
    def _valid_hours(self, data):
        opening_time = data.get("opening_time")
        closing_time = data.get("closing_time")
        if opening_time and closing_time and opening_time >= closing_time:
            raise serializers.ValidationError(
                {"closing_time": "Closing time must be later than opening time"}
            )
        return data

    def get_days_of_operation(self, obj):
        return obj.days_open

    def get_owner_name(self, obj):
        return str(obj.owner)

    def get_manager_names(self, obj):
        return [str(mng) for mng in obj.manager_ids.all()]


class ManagerUpdateMixin:
    def update(self, instance, validated_data):
        managers_data = validated_data.pop("manager_ids", [])
        old_managers = [mng.id for mng in instance.manager_ids.all()]
        add_managers = [mng.id for mng in managers_data if mng.id not in old_managers]
        remove_managers = [mng.id for mng in managers_data if mng.id in old_managers]
        instance = super().update(instance, validated_data)
        instance.manager_ids.add(*add_managers)
        instance.manager_ids.remove(*remove_managers)
        return instance


class StoreSerializer(
    serializers.ModelSerializer, BaseSerializerMixin, ManagerUpdateMixin
):
    days_of_operation = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    owner = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), required=False
    )
    manager_names = serializers.SerializerMethodField()
    name = serializers.CharField(required=False, allow_blank=False)
    address = serializers.CharField(required=False, allow_blank=False)
    city = serializers.CharField(required=False, allow_blank=False)
    state_abbrv = serializers.CharField(
        max_length=2, style={"input_type": "string"}, required=False, allow_blank=False
    )
    plz = serializers.CharField(required=False, allow_blank=False)
    opening_time = serializers.TimeField(required=False)
    closing_time = serializers.TimeField(required=False)
    montag = serializers.BooleanField(required=False)
    dienstag = serializers.BooleanField(required=False)
    mittwoch = serializers.BooleanField(required=False)
    donnerstag = serializers.BooleanField(required=False)
    freitag = serializers.BooleanField(required=False)
    samstag = serializers.BooleanField(required=False)
    sonntag = serializers.BooleanField(required=False)
    manager_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=True, required=False
    )

    class Meta:
        model = Store
        include = ["days_of_operation"]
        fields = "__all__"
        write_only_fields = [
            "manager_ids",
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        ]

    def to_internal_value(self, data):
        self._check_unknown_fields(data)
        return super().to_internal_value(data)

    def validate_state_abbrv(self, value):
        if value not in Store.STATES:
            raise serializers.ValidationError(
                f"'{value}' is an invalid state abbreviation"
            )
        return value

    def validate_name(self, value):
        # I think this is where the parser is interacting with things
        if not value.strip():
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def validate_address(self, value):
        has_number = any(char.isdigit() for char in value)
        has_text = any(char.isalpha() for char in value)

        if not (has_number and has_text):
            raise serializers.ValidationError(
                "Address must contain both numbers and text."
            )

        return value

    def validate_plz(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PLZ must contain only numbers")
        if len(value) != 5:
            raise serializers.ValidationError("PLZ must be exactly 5 digits")
        return value

    def validate(self, data):
        data = self._valid_hours(data)
        data = super().validate(data)
        return data


class DaysSerializer(serializers.ModelSerializer, BaseSerializerMixin):
    id = serializers.IntegerField(read_only=True, required=False)
    name = serializers.CharField(read_only=True, required=False)
    owner_name = serializers.SerializerMethodField(required=False)
    manager_names = serializers.SerializerMethodField(required=False)
    days_of_operation = serializers.SerializerMethodField(required=False)
    montag = serializers.BooleanField(required=False)
    dienstag = serializers.BooleanField(required=False)
    mittwoch = serializers.BooleanField(required=False)
    donnerstag = serializers.BooleanField(required=False)
    freitag = serializers.BooleanField(required=False)
    samstag = serializers.BooleanField(required=False)
    sonntag = serializers.BooleanField(required=False)

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "owner_name",
            "manager_names",
            "days_of_operation",
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        ]

    def to_internal_value(self, data):
        self._check_unknown_fields(data)
        return super().to_internal_value(data)


class HoursSerializer(serializers.ModelSerializer, BaseSerializerMixin):
    id = serializers.IntegerField(read_only=True, required=False)
    name = serializers.CharField(read_only=True, required=False)
    owner_name = serializers.SerializerMethodField()
    manager_names = serializers.SerializerMethodField()
    days_of_operation = serializers.SerializerMethodField()
    opening_time = serializers.TimeField(required=False)
    closing_time = serializers.TimeField(required=False)

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "owner_name",
            "manager_names",
            "days_of_operation",
            "opening_time",
            "closing_time",
        ]

    def validate(self, data):
        data = self._valid_hours(data)
        return super().validate(data)

    def to_internal_value(self, data):
        self._check_unknown_fields(data)
        return super().to_internal_value(data)


class ManagersSerializer(
    serializers.ModelSerializer, BaseSerializerMixin, ManagerUpdateMixin
):
    id = serializers.IntegerField(read_only=True, required=False)
    name = serializers.CharField(read_only=True, required=False)
    owner_name = serializers.SerializerMethodField()
    manager_names = serializers.SerializerMethodField()
    days_of_operation = serializers.SerializerMethodField()
    manager_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=True, required=False
    )

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "owner_name",
            "manager_names",
            "manager_ids",
            "days_of_operation",
        ]

    def to_internal_value(self, data):
        self._check_unknown_fields(data)
        return super().to_internal_value(data)


class StoreHoursSerializer(serializers.ModelSerializer, BaseSerializerMixin):
    day_display = serializers.CharField(source="get_day_display", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = StoreHours
        fields = [
            "id",
            "store",
            "store_name",
            "day",
            "day_display",
            "opening_time",
            "closing_time",
        ]

    def to_internal_value(self, data):
        self._check_unknown_fields(data)
        return super().to_internal_value(data)

    def validate(self, data):
        data = self._valid_hours(data)
        day = data.get("day")
        if day not in StoreHours.DAYS_OF_WEEK_DICT.items():
            raise serializers.ValidationError(
                f"Day must be one of {StoreHours.DAYS_OF_WEEK_DICT.items()}"
            )
        return super().validate(data)

    def update(self, instance, validated_data):
        day = validated_data.get("day")
        if day and day != instance.day:
            raise serializers.ValidationError(
                f"Cannot change the day. This method only updates the hours of operation on {day}"
            )
        instance = super().update(instance, validated_data)

        return instance
