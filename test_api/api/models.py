from django.db import models


# Create your models here.
class Package(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name + ": " + str(self.price)


class Order(models.Model):
    package = models.ManyToManyField(Package)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
