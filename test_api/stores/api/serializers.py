from rest_framework import serializers
from ..models import Store


class StoreSerializer(serializers.ModelSerializer):
    open_days = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = "__all__"
        include = ["owner", "open_days"]

    def get_open_days(self, obj):
        return obj.days_open

    def get_owner(self, obj):
        return (
            obj.owner.first_name
            + " "
            + obj.owner.last_name
            + " id: "
            + str(obj.owner.id)
        )


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
