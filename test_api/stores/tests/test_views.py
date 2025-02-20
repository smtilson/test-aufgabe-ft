from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from datetime import time

from stores.models import Store

User = get_user_model()

# at the end re-evaluate if you need all this extra shit.
OWNER1_DATA = {
    "email": "owner@example.com",
    "password": "STRONG_password123",
    "first_name": "Owner",
    "last_name": "Test",
}
OWNER2_DATA = {key: value + "1" for key, value in OWNER1_DATA.items()}
MANAGER1_DATA = {
    "email": "manager@example.com",
    "password": "STRONG_password123",
    "first_name": "Manager",
    "last_name": "Test",
}
MANAGER2_DATA = {key: value + "1" for key, value in MANAGER1_DATA.items()}
STORE1_DATA = {
    "name": "Test Store",
    "address": "123 Main St",
    "city": "Test City",
    "state_abbrv": "BE",
    "plz": "12345",
    "opening_time": "09:00:00",
    "closing_time": "17:00:00",
}
STORE2_DATA = {key: value + "1" for key, value in STORE1_DATA.items()}
STORE2_DATA["opening_time"] = "08:00:01"
STORE2_DATA["closing_time"] = "18:00:01"
STORE3_DATA = {key: value + "1" for key, value in STORE2_DATA.items()}
STORE3_DATA["opening_time"] = "08:00:02"
STORE3_DATA["closing_time"] = "19:00:01"


class BaseTestCase(APITestCase):
    def setUp(self):
        self.owner1 = User.objects.create_user(**OWNER1_DATA)
        self.owner2 = User.objects.create_user(**OWNER2_DATA)
        self.manager1 = User.objects.create_user(**MANAGER1_DATA)
        self.manager2 = User.objects.create_user(**MANAGER2_DATA)
        self.store1 = Store.objects.create(owner_id=self.owner1, **STORE1_DATA)
        self.store2 = Store.objects.create(owner_id=self.owner1, **STORE2_DATA)
        self.store3 = Store.objects.create(owner_id=self.owner2, **STORE3_DATA)
        self.store1.manager_ids.add(self.manager1)
        self.store2.manager_ids.add(self.manager2)
        self.token1, _ = Token.objects.get_or_create(user=self.owner1)
        self.token2, _ = Token.objects.get_or_create(user=self.owner2)
        self.token3, _ = Token.objects.get_or_create(user=self.manager1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token1.key}",
            HTTP_ACCEPT="application/json",
        )


# StoreViewSet tests:
class StoreViewSetTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("stores-list")
        # self.store1_url = reverse("store-detail", args=[self.store1.id])
        # self.store2_url = reverse("store-detail", args=[self.store2.id])

    def test_list_stores(self):
        # Test owner1 sees their stores
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        store_ids = {store["id"] for store in response.data["results"]}
        self.assertEqual(store_ids, {self.store1.id, self.store2.id})

        # Test owner2 sees their store
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token2.key}",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.store3.id)

        # Test manager1 sees no stores
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token3.key}",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


# Test create store


# Test retrieve store
# Test update store
# Test delete store
# Test custom messages in responses
# StoreDaysView tests:

# Test list stores with days info
# Test retrieve store days
# Test update store days
# Test custom messages in responses
# StoreHoursView tests:

# Test list stores with hours info
# Test retrieve store hours
# Test update store hours
# Test custom messages in responses
# StoreManagersView tests:

# Test list stores with manager info
# Test retrieve store managers
# Test update store managers
# Test custom messages in responses
