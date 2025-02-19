from rest_framework import serializers
from ..models import Package, Order


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "name", "price"]


class OrderSerializer(serializers.ModelSerializer):
    # To manage the ManyToMany relationship
    # package = serializers.PrimaryKeyRelatedField(
    #   queryset=Package.objects.all(), many=True
    # )
    package = serializers.StringRelatedField(many=True)

    class Meta:
        model = Order
        fields = ["id", "package", "quantity", "total_price"]

    def update(self, instance, validated_data):
        # Handle ManyToMany relationship explicitly
        packages_data = validated_data.pop("package", [])
        instance = super().update(instance, validated_data)
        # Update the ManyToMany relationship
        instance.package.add(
            *[pkg.id for pkg in packages_data]
        )  # `.set()` to replace the relationships
        return instance

    def create(self, validated_data):
        packages_data = validated_data.pop("package", [])
        order = super().create(validated_data)
        order.package.set(packages_data)  # Associate packages with the order
        return order
