from rest_framework import serializers
from ..models import Store, DAYS_OF_WEEK
from users.models import CustomUser


class StoreSerializer(serializers.ModelSerializer):
    days_of_operation = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), required=False
    )
    managers = serializers.SerializerMethodField()
    name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state_abbrv = serializers.CharField(
        max_length=2, style={"input_type": "string"}, required=False
    )
    plz = serializers.CharField(required=False)
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
        raise_unknown_fields = True
        include = ["days_of_operation"]
        fields = "__all__"
        write_only_fields = [
            "manger_ids",
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        ]

    def get_days_of_operation(self, obj):
        return obj.days_open

    def get_owner(self, obj):
        return str(obj.owner_id)

    def get_managers(self, obj):
        return [str(mng) for mng in obj.manager_ids.all()]

    def update(self, instance, validated_data):
        managers_data = validated_data.pop("manager_ids", [])
        old_managers = [mng.id for mng in instance.manager_ids.all()]
        add_managers = [mng.id for mng in managers_data if mng.id not in old_managers]
        remove_managers = [mng.id for mng in managers_data if mng.id in old_managers]
        instance = super().update(instance, validated_data)
        instance.manager_ids.add(*add_managers)
        instance.manager_ids.remove(*remove_managers)
        return instance

    def to_internal_value(self, data):
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

        return super().to_internal_value(data)

    def is_creation(self):
        return self.context.get("request") and self.context["request"].method == "POST"

    def check_required_fields(self, data):
        if not self.is_creation():
            return
        required_fields = ["name", "owner_id", "address", "city", "state_abbrv"]
        errors = {}
        for field in required_fields:
            if field not in data:
                errors[field] = f"The field {field} is required for store creation."

        if errors:
            raise serializers.ValidationError(errors)

    def check_open_closing_times(self, data):
        opening_time = data.get("opening_time")
        closing_time = data.get("closing_time")
        if opening_time and closing_time and opening_time >= closing_time:
            raise serializers.ValidationError(
                {"closing_time": "Closing time must be later than opening time"}
            )

    def check_empty_update(self, data):
        if self.context["request"].method == "PATCH":
            for field_name, value in data.items():
                if isinstance(value, str) and not value.strip():
                    raise serializers.ValidationError(
                        {field_name: "You cannot update a field to be empty"}
                    )

    def validate_state_abbrv(self, value):
        if value not in Store.STATES:
            raise serializers.ValidationError(
                f"'{value}' is an invalid state abbreviation"
            )
        return value

    def validate_name(self, value):
        # something is catching this error before I get to here.
        if not isinstance(value, str):
            raise serializers.ValidationError("Name must be a string.")
        elif not value.strip():
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
        self.check_empty_update(data)
        self.check_required_fields(data)
        self.check_open_closing_times(data)
        data = super().validate(data)
        return data


class DaysSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, required=False)
    name = serializers.CharField(read_only=True, required=False)
    owner = serializers.SerializerMethodField(required=False)
    managers = serializers.SerializerMethodField(required=False)
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
        raise_unknown_fields = True
        fields = [
            "id",
            "name",
            "owner",
            "managers",
            "days_of_operation",
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        ]

    def get_owner(self, obj):
        return str(obj.owner_id)

    def get_managers(self, obj):
        return [str(mng) for mng in obj.manager_ids.all()]

    def get_days_of_operation(self, obj):
        return obj.days_open

    def to_internal_value(self, data):
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

        return super().to_internal_value(data)


class HoursSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, required=False)
    name = serializers.CharField(read_only=True, required=False)
    owner = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()
    days_of_operation = serializers.SerializerMethodField()
    opening_time = serializers.TimeField(required=False)
    closing_time = serializers.TimeField(required=False)

    class Meta:
        model = Store
        raise_on_validation_error = True
        fields = [
            "id",
            "name",
            "owner",
            "managers",
            "days_of_operation",
            "opening_time",
            "closing_time",
        ]

    def get_owner(self, obj):
        return str(obj.owner_id)

    def get_managers(self, obj):
        return [str(mng) for mng in obj.manager_ids.all()]

    def get_days_of_operation(self, obj):
        return obj.days_open

    def validate(self, data):
        data = super().validate(data)
        opening_time = data.get("opening_time")
        closing_time = data.get("closing_time")
        if opening_time and closing_time and opening_time >= closing_time:
            raise serializers.ValidationError(
                {"closing_time": "Closing time must be later than opening time"}
            )
        return data

    def to_internal_value(self, data):
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

        return super().to_internal_value(data)


class ManagersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, required=False)
    name = serializers.CharField(read_only=True, required=False)
    owner = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()
    days_of_operation = serializers.SerializerMethodField()
    manager_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=True, required=False
    )

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "owner",
            "managers",
            "manager_ids",
            "days_of_operation",
        ]
        raise_on_validation_error = True

    def get_owner(self, obj):
        return str(obj.owner_id)

    def get_managers(self, obj):
        return [str(mng) for mng in obj.manager_ids.all()]

    def get_days_of_operation(self, obj):
        return obj.days_open

    def update(self, instance, validated_data):
        managers_data = validated_data.pop("manager_ids", [])
        old_managers = [mng.id for mng in instance.manager_ids.all()]
        add_managers = [mng.id for mng in managers_data if mng.id not in old_managers]
        remove_managers = [mng.id for mng in managers_data if mng.id in old_managers]
        instance = super().update(instance, validated_data)
        instance.manager_ids.add(*add_managers)
        instance.manager_ids.remove(*remove_managers)
        return instance

    def to_internal_value(self, data):
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

        return super().to_internal_value(data)
