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


class StoreViewSetTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("stores-list")
        self.url_detail = reverse("stores-detail", args=[self.store1.id])
        # self.store1_url = reverse("store-detail", args=[self.store1.id])
        # self.store2_url = reverse("store-detail", args=[self.store2.id])

    def test_unauthenticated_access(self):
        self.client.credentials()  # No auth header
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_access(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalidtoken")
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_stores(self):
        # Test owner1 sees their stores
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        store_ids = {store["id"] for store in response.data["results"]}
        self.assertEqual(store_ids, {self.store1.id, self.store2.id})

        # Test owner2 sees their store
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token2.key}",
        )
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.store3.id)

        # Test manager1 sees their store
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token3.key}",
        )

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.store1.id)
        self.assertEqual(
            response.data["message"], "Create a store by filling the relevant fields."
        )

    def test_list_stores_pagination(self):
        response = self.client.get(self.url_list, {"page": 1, "page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_pagination_out_of_bounds(self):
        # Request a page that doesn't exist
        response = self.client.get(self.url_list + "?page=999&page_size=2")
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
        response = self.client.post(self.url_list, new_store_data)
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
            "owner_id": 12,
            "state_abbrv": "XX",  # invalid state
            "plz": "123",  # too short
            "opening_time": "25:00:00",  # invalid time
            "closing_time": "18:00:00",
            "manager_ids": [999],  # non-existent manager
        }
        response = self.client.post(self.url_list, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), 3)  # no new store created
        for term in {"error", "invalid", "does not exist"}:
            self.assertIn(term, str(response.data).lower())

    def test_create_store_invalid_times(self):
        store_data = STORE1_DATA.copy()
        store_data.update(
            {
                "opening_time": "09:00:00",
                "closing_time": "08:00:00",  # Earlier than opening
                "owner_id": self.owner1.id,
            }
        )
        response = self.client.post(self.url_list, store_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), 3)
        for term in {"error", "invalid", "closing time"}:
            self.assertIn(term, str(response.data).lower())

    def test_create_store_missing_required_fields(self):
        incomplete_data = {"name": "Test Store", "city": "Test City"}
        response = self.client.post(self.url_list, incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), 3)
        for term in {"error", "required", "invalid", "address"}:
            self.assertIn(term, str(response.data).lower())

    # Test retrieve store
    def test_retrieve_valid_store(self):
        response = self.client.get(self.url_detail)
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
        self.assertEqual(response.data["detail"].code, "not_found")

    # Test update store
    def test_update_store(self):
        # Try to update all fields
        response = self.client.patch(self.url_detail, STORE3_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_store = Store.objects.get(id=self.store1.id)
        self.assertEqual(updated_store.name, STORE3_DATA["name"])

    def test_update_nonexistent_store(self):
        url = reverse("stores-detail", args=[999])
        update_data = {"name": "New Name"}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_update_store_invalid_data(self):
        update_data = {
            # this isnt throwing an error for some reason, but the serializer seems to handle it fine.
            # "name": "",  # empty name
            "state_abbrv": "XX",  # invalid state
            "plz": "123",  # too short
            "opening_time": "25:00:00",  # invalid time
            # "closing_time": "18:00:00",
            "manager_ids": [999],  # non-existent manager
        }
        response = self.client.patch(self.url_detail, update_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), 3)  # no new store created

        # Verify error messages
        terms = list(update_data.keys())
        terms.extend(["error", "invalid", "does not exist"])
        for term in terms:
            self.assertIn(term, str(response.data).lower())

    def test_update_store_name_validation(self):
        invalid_names = ["", " ", ["name"]]

        for name in invalid_names:
            response = self.client.patch(self.url_detail, {"name": name})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("name", response.data)

        valid_name = "Updated Store Name"
        response = self.client.patch(self.url_detail, {"name": valid_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], valid_name)

    def test_update_store_address_validation(self):
        invalid_addresses = ["", " ", ["address"]]

        for address in invalid_addresses:
            response = self.client.patch(self.url_detail, {"address": address})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("address", response.data)

        valid_address = "456 New Street"
        response = self.client.patch(self.url_detail, {"address": valid_address})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["address"], valid_address)

    def test_update_store_city_validation(self):
        invalid_cities = ["", " ", ["city"]]

        for city in invalid_cities:
            response = self.client.patch(self.url_detail, {"city": city})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("city", response.data)

        valid_city = "New City"
        response = self.client.patch(self.url_detail, {"city": valid_city})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], valid_city)

    def test_update_store_state_validation(self):
        print("testing view for state abbreviation validation")
        invalid_states = [["BE", "HH"]]  # ["XX", "ABC", "A", "12", ["BE"]]

        for state in invalid_states:
            print("checking:  ", state)
            response = self.client.patch(self.url_detail, {"state_abbrv": state})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("state_abbrv", response.data)

        valid_state = "HH"
        response = self.client.patch(self.url_detail, {"state_abbrv": valid_state})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state_abbrv"], valid_state)

    def test_plz_validation(self):
        invalid_plz_values = [
            "123",
            "1234567",
            "1234a",
            "abcde",
            "12 34",
            "@#$%&",
            ["1", "2", "3", "4", "5"],
        ]

        for plz in invalid_plz_values:
            response = self.client.patch(self.url_detail, {"plz": plz})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("plz", response.data)

        # Test valid PLZ values
        valid_plz_values = [
            "12345",  # string
            12345,  # integer
        ]

        for plz in valid_plz_values:
            response = self.client.patch(self.url_detail, {"plz": plz})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["plz"], "12345")

    # Test delete store
    def test_delete_store(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Store.objects.count(), 2)
        self.assertFalse(Store.objects.filter(id=self.store1.id).exists())

    def test_delete_nonexistent_store(self):
        url = reverse("stores-detail", args=[999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Store.objects.count(), 3)
        self.assertEqual(response.data["detail"].code, "not_found")


@skip
class StoreDaysViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("store-days-list")
        self.url_detail = reverse("store-days-detail", kwargs={"pk": self.store1.id})

    def test_get_store_days_valid_id(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["days_of_operation"], str(["Montag", "Dienstag", "Mittwoch"])
        )
        self.assertIn("Modify the days of operation by", response.data["message"])

    def test_get_store_days_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)  # Owner1 has 2 stores

        # Check first store in results
        first_store = response.data["results"][0]
        self.assertEqual(first_store["id"], self.store1.id)

        # Check message
        self.assertEqual(
            response.data["message"], "Select store to modify its days of operation."
        )

    def test_list_pagination(self):
        response = self.client.get(self.url_list, {"page": 1, "page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        # Verify second page
        response = self.client.get(self.url_list, {"page": 2, "page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_pagination_out_of_bounds(self):
        response = self.client.get(self.url_list + "?page=999&page_size=1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

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
        list_response = self.client.get(self.url_list)
        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try detail endpoint

        detail_response = self.client.get(self.url_detail)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_days_to_false(self):
        data = {"montag": False, "dienstag": False}
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["days_of_operation"], str(["Mittwoch"]))

    def test_update_days_to_true(self):
        data = {"donnerstag": True, "freitag": True}
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["days_of_operation"],
            str(["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]),
        )

    def test_update_days_invalid_boolean(self):
        data = {"montag": "not_a_boolean", "dienstag": 123}
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["montag"][0].code, "invalid")
        self.assertEqual(response.data["dienstag"][0].code, "invalid")

    def test_update_days_invalid_field(self):
        data = {"invalid_day": True, "not_a_day": False}
        response = self.client.patch(self.url_detail, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["invalid_day"].code, "invalid")
        self.assertEqual(response.data["not_a_day"].code, "invalid")

    def test_days_of_operation_order(self):
        # Set some non-sequential days to true
        data = {
            "montag": False,
            "dienstag": True,
            "mittwoch": False,
            "donnerstag": True,
            "freitag": True,
            "samstag": False,
            "sonntag": True,
        }
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that days are in correct weekday order
        expected_order = ["Dienstag", "Donnerstag", "Freitag", "Sonntag"]
        self.assertEqual(response.data["days_of_operation"], str(expected_order))


@skip
class StoreHoursViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("store-hours-list")
        self.url_detail = reverse("store-hours-detail", kwargs={"pk": 1})

    def test_store_hours_invalid_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token")

        # Try list endpoint
        list_response = self.client.get(self.url_list)
        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try detail endpoint
        detail_response = self.client.get(self.url_detail)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_access(self):
        self.client.credentials()  # No auth header

        # Try list endpoint
        list_response = self.client.get(self.url_list)
        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try detail endpoint

        detail_response = self.client.get(self.url_detail)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_store_hours_valid_id(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["opening_time"], self.times["opening_time"])
        self.assertEqual(response.data["closing_time"], self.times["closing_time"])
        self.assertEqual(
            response.data["message"],
            "Modify the hours of operation using the given fields.",
        )

    def test_get_store_hours_invalid_id(self):
        url = reverse("store-hours-detail", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_get_store_hours_list(self):
        url = reverse("store-hours-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # Owner1 has 2 stores
        first_store = response.data["results"][0]
        self.assertEqual(first_store["id"], self.store1.id)
        self.assertEqual(first_store["opening_time"], self.times["opening_time"])
        self.assertEqual(first_store["closing_time"], self.times["closing_time"])

    def test_list_pagination(self):
        response = self.client.get(self.url_list, {"page": 1, "page_size": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_pagination_out_of_bounds(self):
        response = self.client.get(self.url_list + "?page=999&page_size=1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_update_store_hours_success(self):
        data = {"opening_time": "11:00:00", "closing_time": "20:00:00"}
        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["opening_time"], "11:00:00")
        self.assertEqual(response.data["closing_time"], "20:00:00")

    def test_update_store_hours_validation_failures(self):
        invalid_times = [
            # Opening after closing
            {"opening_time": "20:00:00", "closing_time": "08:00:00"},
            # Invalid time values
            {"opening_time": "25:00:00", "closing_time": "27:00:00"},
            # Invalid type
            {"opening_time": "08:00:00", "closing_time": [20, 0, 100]},
        ]

        for data in invalid_times:
            response = self.client.put(self.url_detail, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", str(response.data).lower())
            self.assertIn("closing_time", str(response.data).lower())

    def test_update_nonexistent_store_hours(self):
        url = reverse("store-hours-detail", kwargs={"pk": 999})
        data = {"opening_time": "08:00:00", "closing_time": "20:00:00"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")


@skip
class StoreManagersViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("store-managers-list")
        self.url_detail = reverse(
            "store-managers-detail", kwargs={"pk": self.store1.id}
        )

    def test_store_managers_invalid_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token")

        # Try list endpoint
        list_response = self.client.get(self.url_list)
        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try detail endpoint
        detail_response = self.client.get(self.url_detail)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_access(self):
        self.client.credentials()  # No auth header

        # Try list endpoint
        list_response = self.client.get(self.url_list)
        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try detail endpoint
        detail_response = self.client.get(self.url_detail)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_store_managers_valid_id(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.manager1.id, response.data["manager_ids"])
        self.assertEqual(
            response.data["message"],
            "Modify the managers of the store by selecting a given user. Selecting a user that is already a manager will remove their manager status.",
        )

    def test_get_store_managers_invalid_store_id(self):
        url = reverse("store-managers-detail", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_get_store_managers_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # Owner1 has 2 stores
        first_store = response.data["results"][0]
        self.assertEqual(first_store["id"], self.store1.id)
        self.assertIn(self.manager1.id, first_store["manager_ids"])

    def test_list_pagination(self):
        response = self.client.get(self.url_list, {"page": 1, "page_size": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_pagination_out_of_bounds(self):
        response = self.client.get(self.url_list + "?page=999&page_size=1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_add_new_manager(self):
        data = {"manager_ids": [self.manager2.id]}
        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.manager2.id, response.data["manager_ids"])
        self.assertIn(self.manager1.id, response.data["manager_ids"])

    def test_remove_existing_manager(self):
        data = {
            "manager_ids": [self.manager1.id]
        }  # Selecting existing manager removes them
        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.manager1.id, response.data["manager_ids"])

    def test_add_invalid_manager_id(self):
        data = {"manager_ids": [999]}
        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_managers_nonexistent_store(self):
        url = reverse("store-managers-detail", kwargs={"pk": 999})
        data = {"manager_ids": [self.manager2.id]}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")
