from django.db import models


# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    managers = models.ManyToManyField("users.CustomUser", related_name="managed_stores")
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
