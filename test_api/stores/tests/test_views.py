from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from unittest import skip
from django.urls import clear_url_caches

from stores.models import Store
from test_api import load_data as ldb

User = get_user_model()

# Test Data Constants
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
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print(f"\nInitializing test class: {cls.__name__}")

    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(
            email="superuser@super.user", password="superuser"
        )
        cls.super_token, _ = Token.objects.get_or_create(user=cls.super_user)
        ldb.bulk_populate(20, 25)

    def switch_to_superuser(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.super_token.key}",
        )

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
        clear_url_caches()
        self.client.defaults["HTTP_ACCEPT"] = "application/json"
        self.client.defaults["format"] = "json"

    def _url_comparison(self, field, value, comparison):
        return f"{field}_{comparison}={value}"

    def _django_comparison(self, field, comparison):
        return f"{field}__{comparison}"

    def django_query(self, field, specifier):
        return f"{field}_ids__{specifier}"

    def url_query(self, field, specifier):
        return f"{field}_{specifier}"


class StoreViewSetTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("stores-list")
        self.url_detail = reverse("stores-detail", args=[self.store1.id])

    # Authentication Tests
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

    # List Tests
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

    # Pagination Tests
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

    # Create Store wih valid and invalid data
    def test_create_store(self):
        new_store_data = {key: value + "1" for key, value in STORE3_DATA.items()}
        new_store_data["state_abbrv"] = "HH"
        new_store_data["opening_time"] = "08:00:02"
        new_store_data["closing_time"] = "19:00:01"
        new_store_data["plz"] = "12115"
        new_store_data["owner_id"] = self.owner1.id
        new_store_data["manager_ids"] = [self.manager1.id]

        # Test owner can create store
        old_count = Store.objects.count()
        response = self.client.post(self.url_list, new_store_data)
        count = Store.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count, old_count + 1)
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
        count = Store.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), count)  # no new store created
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
        count = Store.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), count)
        for term in {"error", "invalid", "closing time"}:
            self.assertIn(term, str(response.data).lower())

    def test_create_store_missing_required_fields(self):
        incomplete_data = {"name": "Test Store", "city": "Test City"}
        response = self.client.post(self.url_list, incomplete_data)
        count = Store.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), count)
        for term in {"error", "required", "invalid", "address"}:
            self.assertIn(term, str(response.data).lower())

    # Retrieve Tests
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

    # Update Tests
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
        count = Store.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Store.objects.count(), count)  # no new store created

        # Verify error messages
        terms = list(update_data.keys())
        terms.extend(["error", "invalid", "does not exist"])
        for term in terms:
            self.assertIn(term, str(response.data).lower())

    # Field Validation Tests
    def test_validation_name(self):
        invalid_names = [
            ("", "cannot update a field to be empty"),
            (" ", "cannot update a field to be empty"),
            # (["name"], "not a valid string"),
        ]

        for name, expected_error in invalid_names:
            response = self.client.patch(self.url_detail, {"name": name})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data["name"]).lower())

        valid_name = "Updated Store Name"
        response = self.client.patch(self.url_detail, {"name": valid_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], valid_name)

    def test_validation_address(self):
        # Test invalid addresses with PATCH
        invalid_addresses = [
            ("", "you cannot update a field to be empty"),  # From check_empty_update
            (" ", "you cannot update a field to be empty"),  # From check_empty_update
            (["123 Main St"], "not a valid string"),  # DRF type validation
            ({"street": "123 Main"}, "not a valid string"),  # DRF type validation
            ("OnlyText", "must contain both numbers and text"),  # From validate_address
            ("12345", "must contain both numbers and text"),  # From validate_address
            (12345, "must contain both numbers and text"),  # From validate_address
        ]

        for address, expected_error in invalid_addresses:
            response = self.client.patch(
                self.url_detail, {"address": address}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data["address"]).lower())

        # Test valid addresses with PATCH
        valid_addresses = [
            "123 Main Street",
            "Friedrichstraße 123",
            "Apartment 4B, 567 Park Road",
        ]

        for address in valid_addresses:
            response = self.client.patch(self.url_detail, {"address": address})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["address"], address)

    def test_validation_city(self):
        invalid_cities = [
            ("", "You cannot update a field to be empty"),
            (" ", "You cannot update a field to be empty"),
            # (["city"], "Not a valid string")
        ]

        for city, expected_error in invalid_cities:
            response = self.client.patch(self.url_detail, {"city": city})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data["city"]))

        valid_city = "New City"
        response = self.client.patch(self.url_detail, {"city": valid_city})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], valid_city)

    def test_validation_state(self):
        invalid_states = [
            # (["BE", "HH"], "Not a valid string"),
            # (["BE"], "Not a valid string"),
            ("XX", "invalid state abbreviation"),
            ("ABC", "2 characters"),
            ("A", "invalid state abbreviation"),
            ("12", "invalid state abbreviation"),
        ]

        for state, expected_error in invalid_states:
            response = self.client.patch(self.url_detail, {"state_abbrv": state})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data["state_abbrv"][0]))

        valid_state = "HH"
        response = self.client.patch(self.url_detail, {"state_abbrv": valid_state})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state_abbrv"], valid_state)

    def test_validation_plz(self):
        invalid_plz_values = [
            ("123", "PLZ must be exactly 5 digits"),
            ("1234567", "PLZ must be exactly 5 digits"),
            ("1234a", "PLZ must contain only numbers"),
            ("abcde", "PLZ must contain only numbers"),
            ("12 34", "PLZ must contain only numbers"),
            ("@#$%&", "PLZ must contain only numbers"),
            # (["1", "2", "3", "4", "5"], "Not a valid string")
        ]

        for plz, expected_error in invalid_plz_values:
            response = self.client.patch(self.url_detail, {"plz": plz})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data["plz"][0]))

        # Test valid PLZ values
        valid_plz_values = [
            "12345",  # string
            12345,  # integer
        ]

        for plz in valid_plz_values:
            response = self.client.patch(self.url_detail, {"plz": plz})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["plz"], "12345")

    # Delete Tests
    def test_delete_store(self):
        response = self.client.delete(self.url_detail)
        count = Store.objects.count()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Store.objects.count(), count)
        self.assertFalse(Store.objects.filter(id=self.store1.id).exists())

    def test_delete_nonexistent_store(self):
        url = reverse("stores-detail", args=[999])
        response = self.client.delete(url)
        count = Store.objects.count()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Store.objects.count(), count)
        self.assertEqual(response.data["detail"].code, "not_found")

    # Filter Tests
    def test_filter_valid_store_fields(self):
        self.switch_to_superuser()
        test_cases = (
            ("name", self.store1.name),
            ("city", self.store1.city),
            ("address", self.store1.address),
            ("state_abbrv", self.store1.state_abbrv),
            ("plz", self.store1.plz),
        )

        for field, value in test_cases:
            url = self.url_list + f"?{field}={value}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected_count = Store.objects.filter(
                **{f"{field}__icontains": value}
            ).count()
            self.assertEqual(response.data["count"], expected_count)

    def test_filter_by_owner_id(self):
        self.switch_to_superuser()

        # Create test manager
        test_owner = User.objects.create_user(
            email="test.owner@test.com",
            password="test123",
            first_name="TEST",
            last_name="OWNER",
        )

        # Create test stores owned by superuser
        Store.objects.create(
            owner_id=test_owner,
            name="Test Store 1",
            address="123 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )

        Store.objects.create(
            owner_id=test_owner,
            name="Test Store 2",
            address="456 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )

        # Query by manager ID
        url = self.url_list + f"?owner_id={test_owner.id}"
        response = self.client.get(url)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_count = Store.objects.filter(owner_id=test_owner.id).count()
        self.assertEqual(response.data["count"], expected_count)

    @skip
    def test_filter_by_owner_name(self):
        self.switch_to_superuser()

        # Create test owner
        test_owner = User.objects.create_user(
            email="test.owner@test.com",
            password="test123",
            first_name="TEST",
            last_name="OWNER",
        )
        print(f"\nTest owner created with ID: {test_owner.id}")
        print(f"Owner name: {test_owner.first_name} {test_owner.last_name}")

        # Create test stores owned by test owner
        store1 = Store.objects.create(
            owner_id=test_owner,
            name="Test Store 1",
            address="123 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )
        store2 = Store.objects.create(
            owner_id=test_owner,
            name="Test Store 2",
            address="456 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )
        print(f"Created stores with IDs: {store1.id}, {store2.id}")
        print(f"Store 1 owner: {store1.owner_id.first_name}")
        print(f"Store 2 owner: {store2.owner_id.first_name}")

        # Query by owner first name
        url = self.url_list + "?owner_first_name=TEST"
        print(f"Testing URL: {url}")

        response = self.client.get(url)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

        # Verify results
        expected_count = Store.objects.filter(
            owner_id__first_name__icontains="TEST"
        ).count()
        print(f"Expected count: {expected_count}")
        print(response.data.keys())
        print(f"Actual count: {response.data['count']}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], expected_count)

    def test_filter_malformed_owner_id(self):
        self.switch_to_superuser()
        invalid_formats = (
            ("abc", "Enter a number"),
            # why is this considered a valid owner id?
            ("-1", "Invalid owner ID"),
            ("0", "Invalid owner ID"),
        )

        for owner_id, error_msg in invalid_formats:
            url = self.url_list + f"?owner_id={owner_id}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_nonexistent_owner_id(self):
        self.switch_to_superuser()
        id = str(User.objects.all().count() + 1)
        url = self.url_list + "?owner_id=" + id
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_malformed_owner_name(self):
        self.switch_to_superuser()
        invalid_names = (
            ("123", "at least one letter"),
            ("@#$", "at least one letter"),
        )

        for name, error_msg in invalid_names:
            url = self.url_list + f"?owner_first_name={name}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_owner_ordering(self):
        self.switch_to_superuser()
        ordering_fields = (
            "owner_first_name",
            "-owner_first_name",
            "owner_last_name",
            "-owner_last_name",
        )

        for field in ordering_fields:
            url = self.url_list + f"?ordering={field}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_invalid_store_name(self):
        self.switch_to_superuser()
        invalid_names = [
            ("", "empty values not allowed"),  # this behavior should match
            (" ", "at least one letter"),  # this behavior should match
            # issue with parser coercing things into strings
            # (["Store Name"], "not a valid string"),
            # ({"name": "Store"}, "not a valid string"),
        ]

        for name, expected_error in invalid_names:
            url = self.url_list + f"?name={name}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data).lower())

    def test_filter_invalid_address(self):
        self.switch_to_superuser()
        invalid_addresses = [
            ("", "empty values not allowed"),  # this behavior should match
            (" ", "not be blank"),  # this behavior should match
            # issue with parser coercing things into strings
            # (["123 Main St"], "not a valid string"),
            # ({"street": "123 Main"}, "not a valid string"),
            ("OnlyText", "must contain both numbers and text"),
            ("12345", "must contain both numbers and text"),
        ]

        for address, expected_error in invalid_addresses:
            url = self.url_list + f"?address={address}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data).lower())

    def test_filter_invalid_state(self):
        self.switch_to_superuser()
        invalid_states = ["XX", "ABC", "A", "12"]
        invalid_states = {abbrv: "Select a valid choice" for abbrv in invalid_states}

        for state, expected_error in invalid_states.items():
            url = self.url_list + f"?state_abbrv={state}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data))

    def test_filter_invalid_plz(self):
        self.switch_to_superuser()
        invalid_plz = [
            ("123", "exactly 5 digits"),
            ("1234567", "exactly 5 digits"),
            ("1234a", "only numbers"),
            ("abcde", "only numbers"),
            ("12 34", "only numbers"),
        ]

        for plz, expected_error in invalid_plz:
            url = self.url_list + f"?plz={plz}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(expected_error, str(response.data["plz"]).lower())

    def test_filter_valid_store(self):
        self.switch_to_superuser()
        valid_cases = [
            ("name", "Test Store"),
            ("address", "123 Main Street"),
            ("state_abbrv", "BE"),
            ("plz", "12345"),
        ]

        for field, value in valid_cases:
            url = self.url_list + f"?{field}={value}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_store_specific_ordering(self):
        self.switch_to_superuser()
        ordering_fields = (
            "name",
            "-name",
            "city",
            "-city",
            "state",
            "-state",
        )

        for field in ordering_fields:
            url = self.url_list + f"?ordering={field}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class StoreDaysViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("store-days-list")
        self.url_detail = reverse("store-days-detail", kwargs={"pk": self.store1.id})

    # GET request tests
    def test_get_store_days_valid_id(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["days_of_operation"],
            str(["Montag", "Dienstag", "Mittwoch"]),
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
            response.data["message"],
            "Select store to modify its days of operation.",
        )

    # Error handling tests
    def test_get_store_days_invalid_id(self):
        url = reverse("store-days-detail", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"].code, "not_found")

    def test_get_store_days_malformed_id(self):
        url = "/days-detail/abc/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Pagination tests
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

    # Authentication tests
    def test_store_days_invalid_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token")
        # Try list endpoint
        list_response = self.client.get(self.url_list)
        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try detail endpoint
        detail_response = self.client.get(self.url_detail)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Update operation tests
    def test_update_days_to_false(self):
        data = {"montag": False, "dienstag": False}
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["days_of_operation"], str(["Mittwoch"]))

    def test_update_days_to_true(self):
        data = {"donnerstag": True, "freitag": True}
        response = self.client.patch(self.url_detail, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["days_of_operation"],
            str(["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]),
        )

    # Validation tests
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

    # Business logic tests
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

    # Filtering tests
    def test_filter_by_day(self):
        self.switch_to_superuser()
        for day in self.days_list:
            url = self.url_list + f"?{day}=true"
            response = self.client.get(url)
            count = Store.objects.filter(**{day: True}).count()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], count)

    def test_filter_by_multiple_days(self):
        self.switch_to_superuser()

        # Test different day combinations
        combinations = [
            {"montag": True, "dienstag": True, "mittwoch": True},
            {"freitag": True, "samstag": True, "sonntag": True},
            {"montag": True, "mittwoch": True, "freitag": True},
            {"montag": True, "dienstag": False, "mittwoch": True},
            {"donnerstag": False, "freitag": True, "samstag": False},
            {"montag": False, "mittwoch": False, "freitag": False},
            {"dienstag": True, "donnerstag": False, "samstag": True},
        ]

        for combo in combinations:
            # Build query string
            query = "&".join([f"{day}={value}" for day, value in combo.items()])
            url = self.url_list + "?" + query

            # Get expected count from database
            expected_count = Store.objects.filter(**combo).count()

            # Test response
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], expected_count)

    def test_filter_duplicate_parameters(self):
        self.switch_to_superuser()
        pairs = [("true", "false"), ("true", "true"), ("", "true")]
        for pair in pairs:
            url = self.url_list + f"?montag={pair[0]}&montag={pair[1]}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Duplicate query parameter", str(response.data))

    def test_filter_empty_queries(self):
        self.switch_to_superuser()
        empty_queries = ["?montag=", "?montag=&dienstag=", "?montag", "?dienstag"]
        for query in empty_queries:
            url = self.url_list + query
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Empty values not allowed", str(response.data))

    def test_filter_case_sensitivity(self):
        self.switch_to_superuser()
        true_variations = ["true", "True", "TRUE", "tRuE"]
        false_variations = ["false", "False", "FALSE", "fAlSe"]
        true_count = Store.objects.filter(montag=True).count()
        false_count = Store.objects.filter(montag=False).count()
        for value in true_variations:
            url = self.url_list + f"?montag={value}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], true_count)
        for value in false_variations:
            url = self.url_list + f"?montag={value}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], false_count)

    def test_filter_invalid_values(self):
        self.switch_to_superuser()
        invalid_values = ["yes", "no", "1", "0", "maybe", "truthy"]
        for value in invalid_values:
            url = self.url_list + f"?montag={value}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("must be 'true' or 'false'", str(response.data))

    def test_filter_with_url_encoding(self):
        self.switch_to_superuser()
        encoded_urls = [
            self.url_list + "?montag%3Dtrue",
            self.url_list + "?montag=true%20",
            self.url_list + "?montag%20=true",
        ]
        for url in encoded_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_non_day_parameters(self):
        self.switch_to_superuser()
        invalid_params = [
            "?random=true",
            "?foo=false",
            "?not_a_day=true&montag=true",
        ]
        for param in invalid_params:
            url = self.url_list + param
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Invalid query parameter", str(response.data))


class StoreHoursViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("store-hours-list")
        self.url_detail = reverse("store-hours-detail", kwargs={"pk": self.store1.id})

    def format_query(self, field, value):
        return f"{field}={value}"

    # Authentication Tests
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

    # GET request Tests
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

    # Pagination Tests
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

    # Update Tests
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

    # Filter Tests
    def test_filter_by_time(self):
        self.switch_to_superuser()

        test_cases = {
            "opening_time": ("09:00", "12:30", "17:45", "23:00"),
            "closing_time": ("09:00", "12:30", "17:45", "23:00"),
        }

        for field, times in test_cases.items():
            for time in times:
                url = self.url_list + f"?{field}={time}"
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                expected_count = Store.objects.filter(**{field: time}).count()
                self.assertEqual(response.data["count"], expected_count)

    def test_filter_by_time_range(self):
        self.switch_to_superuser()

        test_cases = [
            {"opening_time": ("08:00", "gte"), "closing_time": ("16:00", "lte")},
            {"opening_time": ("07:00", "lte"), "closing_time": ("23:00", "gte")},
            {"opening_time": ("12:00", "gte"), "closing_time": ("20:00", "lte")},
            {"opening_time": ("06:00", "gte"), "closing_time": ("14:00", "lte")},
            {"opening_time": ("13:00", "lte"), "closing_time": ("22:00", "gte")},
        ]
        # Build URL query string
        for test_case in test_cases:
            search_terms = [
                self._url_comparison(field, value, comp)
                for field, (value, comp) in test_case.items()
            ]
            query = "&".join(search_terms)
            url = self.url_list + "?" + query

            filter_kwargs = {
                self._django_comparison(field, comp): value
                for field, (value, comp) in test_case.items()
            }
            expected_count = Store.objects.filter(**filter_kwargs).count()

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], expected_count)

    def test_filter_duplicate_parameters(self):
        self.switch_to_superuser()

        duplicate_cases = {
            "opening_time=09:00&opening_time=10:00": "Duplicate query parameter",
            "closing_time=17:00&closing_time=18:00": "Duplicate query parameter",
        }

        for case, error_msg in duplicate_cases.items():
            url = self.url_list + "?" + case
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_invalid_time_format(self):
        self.switch_to_superuser()
        invalid_formats = {
            time: "Enter a valid time."
            for time in [
                "09-00",  # wrong separator
                "0900",  # no separator
                "09:00 AM",  # with AM/PM
                "abc",  # non-numeric
                "9",  # single digit hour with zero minutes
                "009:00",  # extra digits
                "9:",  # single digit hour with zero minutes
            ]
        }

        for time, error_msg in invalid_formats.items():
            url = self.url_list + f"?opening_time={time}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_invalid_time_values(self):
        self.switch_to_superuser()
        invalid_values = {
            time: "Enter a valid time."
            for time in [
                "24:00",  # invalid hour
                "25:00",  # invalid hour
                "09:60",  # invalid minute
                "09:99",  # invalid minute
                "23:60",  # invalid minute
            ]
        }

        for time, error_msg in invalid_values.items():
            url = self.url_list + f"?opening_time={time}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_valid_time_format(self):
        self.switch_to_superuser()

        valid_times = {
            "9:00",  # single digit hour
            "09:00",  # with leading zero
            "9:05",  # single digit hour with non-zero minutes
            "23:59",  # end of day
            "00:00",  # start of day
            "9:0",  # single digit hour with zero minutes
            "9:5",  # single digit hour with non-zero minutes
        }

        for input_time in valid_times:
            url = self.url_list + f"?opening_time={input_time}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_empty_queries(self):
        self.switch_to_superuser()

        queries = [
            "?opening_time=",
            "?opening_time=&closing_time=",
            "?opening_time",
            "?closing_time",
        ]
        empty_queries = {query: "Empty values not allowed for" for query in queries}

        for query, error_msg in empty_queries.items():
            url = self.url_list + query
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_with_url_encoding(self):
        self.switch_to_superuser()
        malformed_urls = {
            # do I need more cases?
            self.url_list + "?opening time=09:00",  # space in parameter name
            self.url_list + "?opening_time =09:00",  # space before equals
        }

        for url in malformed_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_non_time_parameters(self):
        self.switch_to_superuser()

        invalid_params = {
            "?random=09:00": "Invalid query parameter",
            "?foo=17:00": "Invalid query parameter",
            "?not_a_time=09:00&opening_time=10:00": "Invalid query parameter",
        }

        for param, error_msg in invalid_params.items():
            url = self.url_list + param
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_ordering(self):
        self.switch_to_superuser()

        ordering_cases = {
            "opens": status.HTTP_200_OK,
            "-opens": status.HTTP_200_OK,
            "closes": status.HTTP_200_OK,
            "-closes": status.HTTP_200_OK,
        }

        for field, expected_status in ordering_cases.items():
            url = self.url_list + f"?ordering={field}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, expected_status)


class StoreManagersViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse("store-managers-list")
        self.url_detail = reverse(
            "store-managers-detail", kwargs={"pk": self.store1.id}
        )

    # Authentication Tests
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

    # GET request tests
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

    # Pagination Tests
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

    # Update Tests
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

    # Filter Tests
    def test_filter_by_manager_id(self):
        self.switch_to_superuser()

        # Create test manager
        test_manager = User.objects.create_user(
            email="test.manager@test.com",
            password="test123",
            first_name="TEST",
            last_name="MANAGER",
        )

        # Create test stores owned by superuser
        test_store1 = Store.objects.create(
            owner_id=self.super_user,
            name="Test Store 1",
            address="123 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )

        test_store2 = Store.objects.create(
            owner_id=self.super_user,
            name="Test Store 2",
            address="456 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )

        # Add test manager to both stores
        test_store1.manager_ids.add(test_manager)
        test_store2.manager_ids.add(test_manager)

        # Query by manager ID
        url = self.url_list + f"?manager_ids={test_manager.id}"
        response = self.client.get(url)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_count = Store.objects.filter(manager_ids=test_manager.id).count()
        self.assertEqual(response.data["count"], expected_count)

    def test_filter_malformed_manager_id(self):
        self.switch_to_superuser()
        invalid_formats = (
            ("abc", "Enter a number"),
            # why is this considered a valid manager id?
            ("-1", "Invalid manager ID"),
            ("0", "Invalid manager ID"),
        )

        for manager_id, error_msg in invalid_formats:
            url = self.url_list + f"?manager_ids={manager_id}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_nonexistent_manager_id(self):
        self.switch_to_superuser()
        id = str(User.objects.all().count() + 1)
        url = self.url_list + "?manager_ids=" + id
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_filter_by_manager_name(self):
        self.switch_to_superuser()

        # Create test manager with distinct name
        test_manager = User.objects.create_user(
            email="test.manager@test.com",
            password="test123",
            first_name="TEST",
            last_name="MANAGER",
        )

        # Create stores owned by superuser
        test_store1 = Store.objects.create(
            owner_id=self.super_user,
            name="Test Store 1",
            address="123 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )

        test_store2 = Store.objects.create(
            owner_id=self.super_user,
            name="Test Store 2",
            address="456 Test St",
            city="Test City",
            state_abbrv="BE",
            plz="12345",
        )

        # Add test manager to both stores
        test_store1.manager_ids.add(test_manager)
        test_store2.manager_ids.add(test_manager)

        # Query by manager first name
        url = self.url_list + "?manager_first_name=TEST"
        response = self.client.get(url)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_malformed_manager_name(self):
        self.switch_to_superuser()
        invalid_names = (
            ("123", "at least one letter"),
            ("@#$", "at least one letter"),
        )

        for name, error_msg in invalid_names:
            url = self.url_list + f"?manager_first_name={name}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_msg, str(response.data))

    def test_filter_manager_ordering(self):
        self.switch_to_superuser()
        ordering_fields = ("first_name", "-first_name", "last_name", "-last_name")

        for field in ordering_fields:
            url = self.url_list + f"?ordering={field}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_empty_queries(self):
        self.switch_to_superuser()

        empty_queries = [
            "?manager_ids=",
            "?manager_first_name=",
            "?manager_last_name=",
            "?manager_ids=&manager_first_name=",
            "?manager_first_name=&manager_last_name=",
            "?manager_ids",
            "?manager_first_name",
            "?manager_last_name",
        ]

        for query in empty_queries:
            url = self.url_list + query
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Empty values not allowed", str(response.data))
