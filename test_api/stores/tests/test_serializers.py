from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError
from datetime import time
from unittest import skip
from unittest.mock import Mock
from stores.models import Store
from stores.api.serializers import (
    StoreSerializer,
    DaysSerializer,
    HoursSerializer,
    ManagersSerializer,
)

# Test data constants
OWNER_DATA = {
    "email": "owner@example.com",
    "password": "STRONG_password123",
    "first_name": "Owner",
    "last_name": "Test",
}

MANAGER_DATA = {
    "email": "manager@example.com",
    "password": "STRONG_password123",
    "first_name": "Manager",
    "last_name": "Test",
}

STORE_DATA = {
    "name": "Test Store",
    "address": "123 Main St",
    "city": "Test City",
    "state_abbrv": "BE",
    "plz": "12345",
}

User = get_user_model()


# Base test case setup
class BaseTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(**OWNER_DATA)
        self.manager = User.objects.create_user(**MANAGER_DATA)
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
        self.store = Store.objects.create(
            owner_id=self.owner, **STORE_DATA, **self.initial_days, **self.times
        )
        self.store.manager_ids.add(self.manager)
        self.setup_context_requests()

    def setup_context_requests(self):
        for method in {"PATCH", "POST", "PUT", "DELETE"}:
            method_request = Mock()
            method_request.method = method
            method_request.user = self.owner
            setattr(self, f"context_{method}", {"request": method_request})


# Store Serializer Tests
class StoreSerializerTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = StoreSerializer(instance=self.store)

    # Store Creation Tests
    def test_create_store_via_serializer(self):
        new_store_data = {
            "name": "New Store",
            "owner_id": self.owner.id,
            "address": "456 Side St",
            "city": "New City",
            "state_abbrv": "HH",
            "plz": "54321",
            "opening_time": "08:00:00",
            "closing_time": "18:00:00",
            "manager_ids": [self.manager.id],
        }
        serializer = StoreSerializer(data=new_store_data, context=self.context_POST)
        self.assertTrue(serializer.is_valid())
        store = serializer.save()

        for key in new_store_data:
            if key in {"owner_id", "manager_ids", "opening_time", "closing_time"}:
                continue
            value = getattr(store, key)
            self.assertEqual(value, new_store_data[key])
        self.assertEqual(store.owner_id, self.owner)
        self.assertIn(self.manager, store.manager_ids.all())
        self.assertEqual(store.opening_time, time(8, 0))
        self.assertEqual(store.closing_time, time(18, 0))

    def test_initial_days(self):
        for day in self.initial_days:
            self.assertEqual(getattr(self.store, day), self.initial_days[day])

    def test_days_of_operation_field(self):
        serializer = StoreSerializer(instance=self.store)
        self.assertEqual(
            serializer.data["days_of_operation"],
            str(["Montag", "Dienstag", "Mittwoch"]),
        )

    def test_owner_field(self):
        self.assertEqual(self.serializer.data["owner"], str(self.owner))

    def test_managers_field(self):
        self.assertEqual(self.serializer.data["managers"], [str(self.manager)])

    # Deserialization Tests
    def test_deserialize_store(self):
        serialized_data = self.serializer.data
        deserializer = StoreSerializer(data=serialized_data, context=self.context_POST)

        self.assertTrue(deserializer.is_valid())
        deserialized_data = deserializer.validated_data
        avoid = {"manager_ids", "closing_time", "opening_time"}
        for key in deserialized_data.keys():
            if key in avoid:
                continue
            self.assertEqual(deserialized_data[key], getattr(self.store, key))

        self.assertEqual(
            deserialized_data["manager_ids"], list(self.store.manager_ids.all())
        )
        opening_time = getattr(self.store, "opening_time")
        self.assertEqual(str(deserialized_data["opening_time"]), opening_time)
        closing_time = str(getattr(self.store, "closing_time"))
        self.assertEqual(str(deserialized_data["closing_time"]), closing_time)

    # Validation Tests
    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            "id",
            "name",
            "owner",
            "owner_id",
            "address",
            "city",
            "state_abbrv",
            "plz",
            "opening_time",
            "closing_time",
            "days_of_operation",
            "updated_at",
            "created_at",
            "manager_ids",
            "managers",
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_validation_field_types(self):
        invalid_data = {
            "name": {123},  # should be string
            "address": ["not", "a", "string"],  # should be string
            "city": {"not": "string"},  # should be string
            "state_abbrv": "XX",  # invalid choice
            "plz": "123abc",  # must be 5 digits
            "opening_time": "25:00:00",  # invalid time
            "closing_time": "invalid",  # invalid time
            "montag": "not_boolean",  # must be boolean
            "dienstag": 1234,  # must be boolean
            "manager_ids": "not_a_list",  # must be list of ids
            "owner_id": "not_an_id",  # must be integer
        }

        serializer = StoreSerializer(data=invalid_data, context=self.context_POST)
        self.assertFalse(serializer.is_valid())
        for field in invalid_data.keys():
            self.assertIn(field, serializer.errors)

    def test_validation_state(self):
        invalid_state_cases = [
            (["BE"], "not a valid string"),
            ("XX", "invalid state"),
            (["BE", "HH"], "not a valid string"),
            (12345, "no more than 2"),
        ]

        serialized_data = self.serializer.data
        # Test invalid cases
        for state, expected_error in invalid_state_cases:
            serialized_data["state_abbrv"] = state
            serializer = StoreSerializer(
                data=serialized_data, context=self.context_PATCH
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn("state_abbrv", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["state_abbrv"]).lower())

        # Test valid case
        serialized_data["state_abbrv"] = "BE"
        serializer = StoreSerializer(data=serialized_data, context=self.context_PATCH)
        self.assertTrue(serializer.is_valid())

    def test_validation_plz(self):
        invalid_plz_cases = [
            ("123", "exactly 5 digits"),
            ("123456", "exactly 5 digits"),
            ("123ab", "only numbers"),
            ("", "to be empty"),
            (["12345"], "not a valid string"),  # single non-string case
        ]

        serialized_data = self.serializer.data
        for plz, expected_error in invalid_plz_cases:
            serialized_data["plz"] = plz
            serializer = StoreSerializer(
                data=serialized_data, context=self.context_PATCH
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn("plz", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["plz"]).lower())

        valid_plz_cases = ["12345", "01234", 99999]

        for plz in valid_plz_cases:
            serialized_data["plz"] = plz
            serializer = StoreSerializer(
                data=serialized_data, context=self.context_PATCH
            )
            self.assertTrue(serializer.is_valid())

    def test_validation_name(self):
        invalid_name_cases = [
            (["Store Name"], "not a valid string"),
            ("", "to be empty"),
            (" ", "to be empty"),
            ({"name": "Store"}, "not a valid string"),
        ]

        valid_names = ["Test Store", "Store 123", "Café Berlin", "Store-Name"]

        serialized_data = self.serializer.data

        # Test invalid cases
        for name, expected_error in invalid_name_cases:
            serialized_data["name"] = name
            serializer = StoreSerializer(
                data=serialized_data, context=self.context_PATCH
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn("name", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["name"]).lower())

        # Test valid cases
        for name in valid_names:
            serialized_data["name"] = name
            serializer = StoreSerializer(
                data=serialized_data, context=self.context_PATCH
            )
            self.assertTrue(serializer.is_valid())
            self.assertEqual(serializer.validated_data["name"], name)

    def test_validation_address(self):
        invalid_address_cases = [
            (["123 Main St"], "not a valid string"),
            ("", "to be empty"),
            (" ", "to be empty"),
            ({"street": "123 Main"}, "not a valid string"),
            (12345, "contain both numbers and text"),
        ]

        valid_addresses = [
            "123 Main Street",
            "Friedrichstraße 123",
            "Apartment 4B, 567 Park Road",
            "Unit 12-345",
        ]

        serialized_data = self.serializer.data

        # Test invalid cases
        for address, expected_error in invalid_address_cases:
            serialized_data["address"] = address
            serializer = StoreSerializer(
                data=serialized_data, context=self.context_PATCH
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn("address", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["address"]).lower())

        for address in valid_addresses:
            serialized_data["address"] = address
            serializer = StoreSerializer(
                data=serialized_data, context=self.context_PATCH
            )
            self.assertTrue(serializer.is_valid())

    def test_validation_time_range(self):
        invalid_cases = [
            (
                {"opening_time": "17:00:00", "closing_time": "09:00:00"},
                ("closing_time", "Closing time must be later than opening time"),
            ),
            (
                {"closing_time": "17:00pm"},
                ("closing_time", "Time has wrong format"),
            ),
            (
                {"opening_time": "25:00:00"},
                ("opening_time", "Time has wrong format"),
            ),
            (
                {"opening_time": "2sdq00"},
                ("opening_time", "Time has wrong format"),
            ),
            (
                {"opening_time": ""},
                ("opening_time", "to be empty"),
            ),
            (
                {"opening_time": ["asd", "123"]},
                ("opening_time", "Time has wrong format"),
            ),
            (
                {"closing_time": 239359},
                ("closing_time", "Time has wrong format"),
            ),
            (
                {"closing_time": 2393},
                ("closing_time", "Time has wrong format"),
            ),
        ]

        for test_data, (error_field, expected_error) in invalid_cases:
            serializer = StoreSerializer(
                self.store, data=test_data, partial=True, context=self.context_PATCH
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn(expected_error, str(serializer.errors[error_field]))

        # Test valid case
        valid_cases = [
            {"closing_time": "17:00:00"},
            {"opening_time": "9:30", "closing_time": "9:45:30"},
        ]

        for valid_times in valid_cases:
            serializer = StoreSerializer(
                self.store, data=valid_times, partial=True, context=self.context_PATCH
            )
            self.assertTrue(serializer.is_valid())

    def test_optional_fields(self):
        required_data = {
            "name": "Test Store",
            "owner_id": self.owner.id,
            "address": "123 Test St",
            "city": "Test City",
            "state_abbrv": "BE",
        }
        serializer = StoreSerializer(data=required_data, context=self.context_POST)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())

    def test_required_fields(self):
        serializer = StoreSerializer(data={}, context=self.context_POST)
        self.assertFalse(serializer.is_valid())

        # Test empty
        required_fields = {"name", "owner_id", "address", "city", "state_abbrv"}
        self.assertEqual(set(serializer.errors.keys()), required_fields)

        # Test partial data
        partial_data = {
            "name": "Test Store",
            "owner_id": self.owner.id,
            "address": "123 Test St",
        }
        serializer = StoreSerializer(data=partial_data, context=self.context_POST)
        self.assertFalse(serializer.is_valid())
        missing_fields = {"city", "state_abbrv"}
        self.assertEqual(set(serializer.errors.keys()), missing_fields)

        # Verify error messages
        for field in serializer.errors:
            self.assertIn(
                "is required for store creation.",
                str(serializer.errors[field]),
            )
            self.assertIn(field, str(serializer.errors[field]))

    # Update and Delete Tests

    def test_add_new_manager(self):
        new_manager_data = {key: value + "1" for key, value in MANAGER_DATA.items()}
        new_manager = User.objects.create_user(**new_manager_data)

        update_data = {"manager_ids": [new_manager.id]}
        serializer = StoreSerializer(
            instance=self.store,
            data=update_data,
            partial=True,
            context=self.context_PATCH,
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertIn(new_manager, updated_store.manager_ids.all())
        self.assertIn(self.manager, updated_store.manager_ids.all())
        self.assertEqual(updated_store.manager_ids.count(), 2)

    def test_remove_existing_manager(self):
        # Verify initial state
        self.assertEqual(self.store.manager_ids.count(), 1)
        self.assertIn(self.manager, self.store.manager_ids.all())

        # Update with empty manager list
        update_data = {"manager_ids": [self.manager.id]}
        serializer = StoreSerializer(
            instance=self.store,
            data=update_data,
            partial=True,
            context=self.context_PATCH,
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        # Verify manager was removed
        self.assertEqual(updated_store.manager_ids.count(), 0)
        self.assertNotIn(self.manager, updated_store.manager_ids.all())

    def test_empty_manager_ids_does_nothing(self):
        # Update with empty manager list
        update_data = {"manager_ids": []}
        serializer = StoreSerializer(
            instance=self.store,
            data=update_data,
            partial=True,
            context=self.context_PATCH,
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        # Verify manager was not removed
        self.assertEqual(updated_store.manager_ids.count(), 1)

    def test_update_owner(self):
        new_owner = User.objects.create_user(
            email="new_owner@test.com",
            password="testpass123",
            first_name="New",
            last_name="Owner",
        )
        update_data = {"owner_id": new_owner.id}
        serializer = StoreSerializer(
            instance=self.store,
            data=update_data,
            partial=True,
            context=self.context_PATCH,
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()
        self.assertEqual(updated_store.owner_id, new_owner)

    def test_unknown_fields(self):
        invalid_data = {"not_a_field": 123, "invalid_field": False}
        serializer = StoreSerializer(
            self.store, data=invalid_data, partial=True, context=self.context_PATCH
        )
        self.assertFalse(serializer.is_valid())
        for value in serializer.errors.values():
            self.assertEqual(value.code, "invalid")
            self.assertIn("field is not recognized", str(value))
        self.assertEqual(invalid_data.keys(), serializer.errors.keys())


class DaysSerializerTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.new_days = {
            "montag": False,
            "dienstag": True,
            "mittwoch": False,
            "donnerstag": True,
            "freitag": False,
            "samstag": False,
            "sonntag": False,
        }
        self.serializer = DaysSerializer(instance=self.store)

    def test_update_days(self):
        serializer = DaysSerializer(self.store, data=self.new_days, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        # Check updated days are True
        for day in self.days_list:
            self.assertEqual(getattr(updated_store, day), self.new_days[day])

    def test_validation_field_type(self):
        invalid_data_cases = [
            ({"montag": "not_a_boolean"}, "Must be a valid boolean"),
            ({"dienstag": 123}, "Must be a valid boolean"),
            ({"mittwoch": ["true"]}, "Must be a valid boolean"),
            ({"donnerstag": {"value": True}}, "Must be a valid boolean"),
        ]

        for test_data, expected_error in invalid_data_cases:
            serializer = DaysSerializer(self.store, data=test_data, partial=True)
            self.assertFalse(serializer.is_valid())
            field = list(test_data.keys())[0]
            self.assertIn(field, serializer.errors)
            self.assertIn(expected_error, str(serializer.errors[field]))

    def test_unknown_fields(self):
        invalid_data = {"not_a_day": True, "invalid_field": False}
        serializer = DaysSerializer(self.store, data=invalid_data, partial=True)
        self.assertFalse(serializer.is_valid())
        for value in serializer.errors.values():
            self.assertEqual(value.code, "invalid")
            self.assertIn("field is not recognized", str(value))
        self.assertEqual(invalid_data.keys(), serializer.errors.keys())

    def test_days_of_operation(self):
        serializer = DaysSerializer(self.store)
        expected_days = [
            day.capitalize() for day, value in self.initial_days.items() if value
        ]
        self.assertEqual(serializer.data["days_of_operation"], str(expected_days))

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            "id",
            "name",
            "owner",
            "managers",
            "days_of_operation",
            "montag",
            "dienstag",
            "mittwoch",
            "donnerstag",
            "freitag",
            "samstag",
            "sonntag",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_read_only_fields(self):
        data = {
            "id": 999,
            "name": "New Name",
        }
        serializer = DaysSerializer(self.store, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        for key, value in data.items():
            self.assertNotEqual(getattr(updated_store, key), value)


class HoursSerializerTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = HoursSerializer(instance=self.store)

    def test_field_type_validations(self):
        invalid_data = {
            "opening_time": ["not_a_time"],
            "closing_time": {"hour": 12},
        }
        serializer = HoursSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

        for field in invalid_data.keys():
            self.assertIn(field, serializer.errors)
            self.assertIn("Time has wrong format", str(serializer.errors[field][0]))

    def test_unknown_fields(self):
        invalid_data = {"not_a_day": "asd", "invalid_field": False}
        serializer = HoursSerializer(self.store, data=invalid_data, partial=True)
        self.assertFalse(serializer.is_valid())
        for value in serializer.errors.values():
            self.assertEqual(value.code, "invalid")
            self.assertIn("field is not recognized", str(value))
        self.assertEqual(invalid_data.keys(), serializer.errors.keys())

    def test_update_hours(self):
        new_hours = {"opening_time": "10:00:00", "closing_time": "20:00:00"}
        serializer = HoursSerializer(self.store, data=new_hours, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.opening_time, time(10, 0))
        self.assertEqual(updated_store.closing_time, time(20, 0))

    def test_validation_time_range(self):
        invalid_cases = [
            (
                {"opening_time": "17:00:00", "closing_time": "09:00:00"},
                ("closing_time", "Closing time must be later than opening time"),
            ),
            (
                {"closing_time": "17:00pm"},
                ("closing_time", "Time has wrong format"),
            ),
            (
                {"opening_time": "25:00:00"},
                ("opening_time", "Time has wrong format"),
            ),
            (
                {"opening_time": "2sdq00"},
                ("opening_time", "Time has wrong format"),
            ),
            (
                {"opening_time": ""},
                ("opening_time", "to be empty"),
            ),
            (
                {"opening_time": ["asd", "123"]},
                ("opening_time", "Time has wrong format"),
            ),
            (
                {"closing_time": 239359},
                ("closing_time", "Time has wrong format"),
            ),
            (
                {"closing_time": 2393},
                ("closing_time", "Time has wrong format"),
            ),
        ]

        for test_data, (error_field, expected_error) in invalid_cases:
            serializer = StoreSerializer(
                self.store, data=test_data, partial=True, context=self.context_PATCH
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn(expected_error, str(serializer.errors[error_field]))

        # Test valid case
        valid_cases = [
            {"closing_time": "17:00:00"},
            {"opening_time": "9:30", "closing_time": "9:45:30"},
        ]

        for valid_times in valid_cases:
            serializer = StoreSerializer(
                self.store, data=valid_times, partial=True, context=self.context_PATCH
            )
            self.assertTrue(serializer.is_valid())

    def test_read_only_fields(self):
        data = {
            "id": 999,
            "name": "New Name",
        }
        serializer = HoursSerializer(self.store, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.id, self.store.id)
        self.assertEqual(updated_store.name, self.store.name)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            "id",
            "name",
            "owner",
            "managers",
            "opening_time",
            "closing_time",
            "days_of_operation",
        }
        self.assertEqual(set(data.keys()), expected_fields)


class ManagersSerializerTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        new_manager_data = {key: value + "1" for key, value in MANAGER_DATA.items()}
        self.new_manager = User.objects.create_user(**new_manager_data)
        self.serializer = ManagersSerializer(instance=self.store)

    def test_initial_managers(self):
        self.assertEqual(self.store.manager_ids.count(), 1)
        self.assertIn(self.manager, self.store.manager_ids.all())

    def test_add_manager(self):
        data = {"manager_ids": [self.new_manager.id]}
        serializer = ManagersSerializer(self.store, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.manager_ids.count(), 2)
        self.assertIn(self.manager, updated_store.manager_ids.all())
        self.assertIn(self.new_manager, updated_store.manager_ids.all())

    def test_remove_manager(self):
        # Initial state verified by test_initial_managers
        data = {"manager_ids": [self.manager.id]}
        serializer = ManagersSerializer(self.store, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.manager_ids.count(), 0)
        self.assertNotIn(self.manager, updated_store.manager_ids.all())

    def test_read_only_fields(self):
        data = {"id": 999, "name": "New Name"}
        serializer = ManagersSerializer(self.store, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.id, self.store.id)
        self.assertEqual(updated_store.name, self.store.name)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            "id",
            "name",
            "owner",
            "managers",
            "manager_ids",
            "days_of_operation",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_field_type_validations(self):
        invalid_data = {
            "manager_ids": "not_a_list",
        }
        serializer = ManagersSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

        self.assertIn("manager_ids", serializer.errors)
        self.assertIn(
            "Expected a list of items", str(serializer.errors["manager_ids"][0])
        )

    def test_unknown_fields(self):
        invalid_data = {"not_a_day": True, "invalid_field": 123}
        serializer = ManagersSerializer(self.store, data=invalid_data, partial=True)
        self.assertFalse(serializer.is_valid())
        for value in serializer.errors.values():
            self.assertEqual(value.code, "invalid")
            self.assertIn("field is not recognized", str(value))
        self.assertEqual(invalid_data.keys(), serializer.errors.keys())
