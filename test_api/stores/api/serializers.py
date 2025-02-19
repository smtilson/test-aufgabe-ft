from rest_framework import serializers
from ..models import Store, DAYS_OF_WEEK
from users.models import CustomUser


class StoreSerializer(serializers.ModelSerializer):
    open_days = serializers.SerializerMethodField()
    # owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects need to filter this?  many=False, read_only=False)
    owner = serializers.SerializerMethodField()
    manager_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=True, read_only=False
    )
    managers = serializers.SerializerMethodField()

    class Meta:
        model = Store
        include = ["open_days"]
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

    def get_open_days(self, obj):
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


class DaysSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    owner = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()
    days_of_operation = serializers.SerializerMethodField()

    class Meta:
        model = Store
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


class HoursSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    owner = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()
    days_of_operation = serializers.SerializerMethodField()

    class Meta:
        model = Store
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


class ManagersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    owner = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()
    days_of_operation = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ["id", "name", "owner", "managers", "manager_ids", "days_of_operation"]

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
