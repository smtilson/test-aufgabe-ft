from rest_framework import serializers
from ..models import Store
from users.models import CustomUser


class StoreSerializer(serializers.ModelSerializer):
    open_days = serializers.SerializerMethodField()
    # owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects need to filter this?  many=False, read_only=False)
    owner_display = serializers.SerializerMethodField()
    managers = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=True, read_only=False
    )

    class Meta:
        model = Store
        include = ["open_days"]
        exclude = [
            "owner",
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

    def get_owner_display(self, obj):
        return (
            obj.owner.first_name
            + " "
            + obj.owner.last_name
            + " id: "
            + str(obj.owner.id)
        )

    def update(self, instance, validated_data):
        managers_data = validated_data.pop("managers", [])
        instance = super().update(instance, validated_data)
        instance.managers.add(*[mng.id for mng in managers_data])
        return instance


class OwnerStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "address",
            "city",
            "state_abbrv",
            "plz",
            "owner",
            "managers",
            "open_days",
            "opening_time",
            "closing_time",
        ]


"""
class StoreHoursSerializer(serializers.Serializer):
    weekday = serializers.ChoiceField(choices=Store.DAYS_OF_WEEK.items())
    open_time = serializers.ModelSerializer.TimeField()
    close_time = serializers.ModelSerializer.TimeField()
    """
