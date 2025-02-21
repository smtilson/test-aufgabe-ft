from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from datetime import time
from unittest import skip
from django.urls import clear_url_caches


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
}
STORE2_DATA = {key: value + "1" for key, value in STORE1_DATA.items()}
STORE3_DATA = {key: value + "1" for key, value in STORE2_DATA.items()}

for key in {"plz", "state_abbrv"}:
    STORE2_DATA[key] = STORE1_DATA[key]
    STORE3_DATA[key] = STORE1_DATA[key]


class BaseTestCase(APITestCase):
    def setUp(self):
        clear_url_caches()
        self.owner1 = User.objects.create_user(**OWNER1_DATA)
        self.owner2 = User.objects.create_user(**OWNER2_DATA)
        self.manager1 = User.objects.create_user(**MANAGER1_DATA)
        self.manager2 = User.objects.create_user(**MANAGER2_DATA)

        self.days_list = [
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        ]
        self.initial_days = {
            "montag": True,
            "dienstag": True,
            "mittwoch": True,
            "donnerstag": False,
            "freitag": False,
            "samstag": False,
            "sonntag": False,
        }
        self.times = {
            "opening_time": "07:00:00",
            "closing_time": "17:00:00",
        }

        self.store1 = Store.objects.create(
            owner_id=self.owner1, **STORE1_DATA, **self.initial_days, **self.times
        )
        self.store2 = Store.objects.create(
            owner_id=self.owner1, **STORE2_DATA, **self.initial_days, **self.times
        )
        self.store3 = Store.objects.create(
            owner_id=self.owner2, **STORE3_DATA, **self.initial_days, **self.times
        )
        self.store1.manager_ids.add(self.manager1)
        self.store2.manager_ids.add(self.manager2)
        self.token1, _ = Token.objects.get_or_create(user=self.owner1)
        self.token2, _ = Token.objects.get_or_create(user=self.owner2)
        self.token3, _ = Token.objects.get_or_create(user=self.manager1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token1.key}",
        )
        self.client.defaults["HTTP_ACCEPT"] = "application/json"


# StoreViewSet tests:


@skip("Skipping StoreViewSetTestCase")
class StoreViewSetTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("stores-list")
        # self.store1_url = reverse("store-detail", args=[self.store1.id])
        # self.store2_url = reverse("store-detail", args=[self.store2.id])

    def test_unauthenticated_access(self):
        self.client.credentials()  # No auth header
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_access(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalidtoken")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

        # Test manager1 sees their store
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token3.key}",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.store1.id)
        self.assertEqual(
            response.data["message"], "Create a store by filling the relevant fields."
        )

    def test_list_stores_pagination(self):
        response = self.client.get(self.url, {"page": 1, "page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_pagination_out_of_bounds(self):
        # Request a page that doesn't exist
        response = self.client.get(self.url + "?page=999&page_size=2")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Check error message
        self.assertEqual(response.data["detail"].code, "not_found")

    # Test create store
    def test_create_store(self):
        new_store_data = {key: value + "1" for key, value in STORE3_DATA.items()}
        new_store_data["state_abbrv"] = "HH"
        new_store_data["opening_time"] = "08:00:02"
        new_store_data["closing_time"] = "19:00:01"
        new_store_data["plz"] = "12115"
        new_store_data["owner_id"] = self.owner1.id
        new_store_data["manager_ids"] = [self.manager1.id]

        # Test owner can create store
        response = self.client.post(self.url, new_store_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.count(), 4)
        # Verify store data
        created_store = Store.objects.get(id=response.data["id"])
        for key, value in new_store_data.items():
            if key in {"manager_ids", "owner_id", "closing_time", "opening_time"}:
                continue
            self.assertEqual(getattr(created_store, key), value)
        self.assertIn(self.manager1, created_store.manager_ids.all())
        self.assertEqual(created_store.owner_id, self.owner1)
        self.assertEqual(
            str(created_store.closing_time), new_store_data["closing_time"]
        )
        self.assertEqual(
            str(created_store.opening_time), new_store_data["opening_time"]
        )
        self.assertNotIn("message", response.data)

    def test_create_store_invalid_data(self):
        invalid_data = {
            "name": "",  # empty name
            "address": "456 Side St",
            "city": "New City",
            "state_abbrv": "XX",  # invalid state
            "plz": "123",  # too short
            "opening_time": "25:00:00",  # invalid time
            "closing_time": "18:00:00",
            "manager_ids": [999],  # non-existent manager
        }
        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), 3)  # no new store created

        # Verify error messages
        self.assertEqual(response.data["name"], ["This field may not be blank."])
        self.assertEqual(response.data["state_abbrv"][0].code, "invalid_choice")
        self.assertEqual(response.data["plz"][0].code, "invalid")
        self.assertEqual(response.data["opening_time"][0].code, "invalid")
        self.assertEqual(response.data["manager_ids"][0].code, "does_not_exist")

    # Test retrieve store
    def test_retrieve_valid_store(self):
        url = reverse("stores-detail", args=[self.store1.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.store1.id)
        for key, value in STORE1_DATA.items():
            self.assertEqual(response.data[key], value)
        self.assertEqual(
            response.data["message"],
            "Modify all aspects of a store by filling the relevant field.",
        )

    def test_retrieve_store_invalid(self):
        url = reverse("stores-detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"].code, "not_found")

    # Test update store
    def test_update_store(self):
        url = reverse("stores-detail", args=[self.store1.id])

        # Try to update all fields
        response = self.client.patch(url, STORE3_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_store = Store.objects.get(id=self.store1.id)

        # Check read-only fields
        read_only_fields = {"id", "owner_id"}
        for field in read_only_fields:
            if field == "id":
                self.assertEqual(updated_store.id, self.store1.id)
            else:
                self.assertEqual(updated_store.owner_id, self.owner1)

        # Check mutable fields
        for key, value in STORE3_DATA.items():
            if key not in read_only_fields:
                if key in ["opening_time", "closing_time"]:
                    self.assertEqual(str(getattr(updated_store, key)), value)
                elif key == "manager_ids":
                    self.assertIn(self.manager2, updated_store.manager_ids.all())
                else:
                    self.assertEqual(getattr(updated_store, key), value)

    def test_update_nonexistent_store(self):
        url = reverse("stores-detail", args=[999])
        update_data = {"name": "New Name"}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_update_store_invalid_data(self):
        url = reverse("stores-detail", args=[self.store1.id])
        update_data = {
            "name": "",  # invalid name
            "address": "456 Side St",
            "city": "New City",
            "state_abbrv": "XX",  # invalid state
            "plz": "123",  # too short
            "opening_time": "25:00:00",  # invalid time
            "closing_time": "18:00:00",
            "manager_ids": [999],  # non-existent manager
        }
        response = self.client.patch(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), 3)  # no new store created

        # Verify error messages
        self.assertEqual(response.data["name"], ["This field may not be blank."])
        self.assertEqual(response.data["state_abbrv"][0].code, "invalid_choice")
        self.assertEqual(response.data["plz"][0].code, "invalid")
        self.assertEqual(response.data["opening_time"][0].code, "invalid")
        self.assertEqual(response.data["manager_ids"][0].code, "does_not_exist")

    # Test delete store
    def test_delete_store(self):
        url = reverse("stores-detail", args=[self.store1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Store.objects.count(), 2)
        self.assertFalse(Store.objects.filter(id=self.store1.id).exists())

    def test_delete_nonexistent_store(self):
        url = reverse("stores-detail", args=[999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Store.objects.count(), 3)
        self.assertEqual(response.data["detail"].code, "not_found")

    # def test_delete_store_by_manager(self):
    #     this should be blocked once I have permissions put in.
    # StoreDaysView tests:


class StoreDaysViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("store-days-detail", kwargs={"pk": self.store1.id})

    def test_store_days_urls(self):
        # Test list URL
        list_url = reverse("store-days-list")
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list_response.data["message"],
            "Select store to modify its days of operation.",
        )

        # Test detail URL
        detail_url = reverse("store-days-detail", kwargs={"pk": self.store1.id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            detail_response.data["message"],
            "Modify the days of operation by selecting or unselecting a given day.",
        )

    def test_get_store_days_valid_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["days_of_operation"], str(["Montag", "Dienstag", "Mittwoch"])
        )  # Adjust according to actual data
        self.assertIn("Modify the days of operation by", response.data["message"])

    def test_get_store_days_list(self):
        url = reverse("store-days-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)  # Owner1 has 2 stores

        # Check first store in results
        first_store = response.data["results"][0]
        self.assertEqual(first_store["id"], self.store1.id)

        # Check message
        self.assertEqual(
            response.data["message"], "Select store to modify its days of operation."
        )

    def test_get_store_days_invalid_id(self):
        url = reverse("store-days-detail", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_get_store_days_malformed_id(self):
        url = "/days-detail/abc/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_store_days_invalid_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token")

        # Try list endpoint
        list_url = reverse("store-days-list")
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try detail endpoint
        detail_url = reverse("store-days-detail", kwargs={"pk": self.store1.id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_days_to_false(self):
        data = {"montag": False, "dienstag": False}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["days_of_operation"], str(["Mittwoch"]))

    def test_update_days_to_true(self):
        data = {"donnerstag": True, "freitag": True}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["days_of_operation"],
            str(["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]),
        )

    def test_update_days_invalid_boolean(self):
        data = {"montag": "not_a_boolean", "dienstag": 123}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["montag"][0].code, "invalid")
        self.assertEqual(response.data["dienstag"][0].code, "invalid")

    def test_update_days_invalid_field(self):
        data = {"invalid_day": True, "not_a_day": False}
        response = self.client.patch(self.url, data)
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["invalid_day"][0].code, "invalid")
        self.assertEqual(response.data["not_a_day"][0].code, "invalid")

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


@skip("Skipping StoreDaysDebugTests")
class StoreDaysDebugTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("store-days-list")
        self.detail_url = reverse("store-days-detail", kwargs={"pk": self.store1.id})

    def test_store_days_list_routes(self):
        # Test first route pattern
        url1 = reverse("store-days-list1")
        print(f"Testing URL1: {url1}")
        response1 = self.client.get(url1)
        print(f"Response1: {response1.content}")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Test second route pattern
        url2 = reverse("store-days-list2")
        print(f"Testing URL2: {url2}")
        response2 = self.client.get(url2)
        print(f"Response2: {response2.content}")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Test third route pattern
        url3 = reverse("store-days-list")
        print(f"Testing URL3: {url3}")
        response3 = self.client.get(url3)
        print(f"Response3: {response3.content}")
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

    @skip("temp")
    def test_store_days_detail_route(self):
        url = reverse("store-days-detail", kwargs={"pk": self.store1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "This is the detail view")
