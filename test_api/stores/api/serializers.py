from rest_framework import serializers
from ..models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


"""
class StoreHoursSerializer(serializers.Serializer):
    weekday = serializers.ChoiceField(choices=Store.DAYS_OF_WEEK.items())
    open_time = serializers.ModelSerializer.TimeField()
    close_time = serializers.ModelSerializer.TimeField()
    """
