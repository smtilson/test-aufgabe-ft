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
from .data import *
from .base import StoreBaseTestCase, APIBaseTestCase


# Store Serializer Tests


class StoreSerializerTest(StoreBaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = StoreSerializer(instance=self.store)

    # Store Creation Tests
    def test_create_store_via_serializer(self):
        new_store_data = {
            "name": "New Store",
            "owner": self.owner1.id,
            "address": "456 Side St",
            "city": "New City",
            "state_abbrv": "HH",
            "plz": "54321",
            "opening_time": "08:00:00",
            "closing_time": "18:00:00",
            "manager_ids": [self.manager1.id],
        }
        serializer = StoreSerializer(data=new_store_data)
        self.assertTrue(serializer.is_valid())
        store = serializer.save()

        for key in new_store_data:
            if key in {"owner", "manager_ids", "opening_time", "closing_time"}:
                continue
            value = getattr(store, key)
            self.assertEqual(value, new_store_data[key])
        self.assertEqual(store.owner, self.owner1)
        self.assertIn(self.manager1, store.manager_ids.all())
        self.assertEqual(store.opening_time, time(8, 0))
        self.assertEqual(store.closing_time, time(18, 0))

    def test_initial_days(self):
        for day in self.initial_days:
            self.assertEqual(getattr(self.store, day), self.initial_days[day])

    def test_days_of_operation_field(self):
        self.assertEqual(
            self.serializer.data["days_of_operation"],
            str(["Montag", "Dienstag", "Mittwoch"]),
        )

    def test_owner_field(self):
        self.assertEqual(self.serializer.data["owner_name"], str(self.owner1))

    def test_managers_field(self):
        self.assertEqual(self.serializer.data["manager_names"], [str(self.manager1)])

    # Deserialization Tests
    def test_deserialize_store(self):
        serialized_data = self.serializer.data
        deserializer = StoreSerializer(data=serialized_data)

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
            "owner_name",
            "owner",
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
            "manager_names",
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
            "owner": "not_an_id",  # must be integer
        }

        serializer = StoreSerializer(data=invalid_data)
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
            serializer = StoreSerializer(data=serialized_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("state_abbrv", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["state_abbrv"]).lower())

        # Test valid case
        serialized_data["state_abbrv"] = "BE"
        serializer = StoreSerializer(data=serialized_data)
        self.assertTrue(serializer.is_valid())

    def test_validation_plz(self):
        invalid_plz_cases = [
            ("123", "exactly 5 digits"),
            ("123456", "exactly 5 digits"),
            ("123ab", "only numbers"),
            ("", "not be blank"),
            (["12345"], "not a valid string"),  # single non-string case
        ]

        serialized_data = self.serializer.data
        for plz, expected_error in invalid_plz_cases:
            serialized_data["plz"] = plz
            serializer = StoreSerializer(data=serialized_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("plz", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["plz"]).lower())

        valid_plz_cases = ["12345", "01234", 99999]

        for plz in valid_plz_cases:
            serialized_data["plz"] = plz
            serializer = StoreSerializer(data=serialized_data)
            self.assertTrue(serializer.is_valid())

    def test_validation_name(self):
        invalid_name_cases = [
            (["Store Name"], "not a valid string"),
            ("", "not be blank"),
            (" ", "not be blank"),
            ({"name": "Store"}, "not a valid string"),
        ]

        valid_names = ["Test Store", "Store 123", "Café Berlin", "Store-Name"]

        serialized_data = self.serializer.data

        # Test invalid cases
        for name, expected_error in invalid_name_cases:
            serialized_data["name"] = name
            serializer = StoreSerializer(data=serialized_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("name", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["name"]).lower())

        # Test valid cases
        for name in valid_names:
            serialized_data["name"] = name
            serializer = StoreSerializer(data=serialized_data)
            self.assertTrue(serializer.is_valid())
            self.assertEqual(serializer.validated_data["name"], name)

    def test_validation_address(self):
        invalid_address_cases = [
            (["123 Main St"], "not a valid string"),
            ("", "not be blank"),
            (" ", "not be blank"),
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
            serializer = StoreSerializer(data=serialized_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("address", serializer.errors)
            self.assertIn(expected_error, str(serializer.errors["address"]).lower())

        for address in valid_addresses:
            serialized_data["address"] = address
            serializer = StoreSerializer(data=serialized_data)
            self.assertTrue(serializer.is_valid())

    # Validation for time range tested in HoursSerializerTest

    # Tests for required and optional fields have moved to the views.
    # The views now handle that logic rather than the serializers.

    # Update and Delete Tests

    def test_add_new_manager(self):
        new_manager = User.objects.create_user(**MANAGER3_DATA)

        update_data = {"manager_ids": [new_manager.id]}
        serializer = StoreSerializer(
            instance=self.store, data=update_data, partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertIn(new_manager, updated_store.manager_ids.all())
        self.assertIn(self.manager1, updated_store.manager_ids.all())
        self.assertEqual(updated_store.manager_ids.count(), 2)

    def test_remove_existing_manager(self):
        # Verify initial state
        self.assertEqual(self.store.manager_ids.count(), 1)
        self.assertIn(self.manager1, self.store.manager_ids.all())

        # Update with managers
        update_data = {"manager_ids": [self.manager1.id]}
        serializer = StoreSerializer(
            instance=self.store, data=update_data, partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        # Verify manager was removed
        self.assertEqual(updated_store.manager_ids.count(), 0)
        self.assertNotIn(self.manager1, updated_store.manager_ids.all())

    def test_empty_manager_ids_does_nothing(self):
        # Update with empty manager list
        update_data = {"manager_ids": []}
        serializer = StoreSerializer(
            instance=self.store, data=update_data, partial=True
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
        update_data = {"owner": new_owner.id}
        serializer = StoreSerializer(
            instance=self.store, data=update_data, partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()
        self.assertEqual(updated_store.owner, new_owner)

    def test_unknown_fields(self):
        invalid_data = {"not_a_field": 123, "invalid_field": False}
        serializer = StoreSerializer(self.store, data=invalid_data, partial=True)
        self.assertFalse(serializer.is_valid())
        for value in serializer.errors.values():
            self.assertEqual(value.code, "invalid")
            self.assertIn("field is not recognized", str(value))
        self.assertEqual(invalid_data.keys(), serializer.errors.keys())


class DaysSerializerTest(StoreBaseTestCase):
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
        # Check initial state
        for day in self.days_list:
            self.assertEqual(getattr(self.store, day), self.initial_days[day])

        serializer = DaysSerializer(self.store, data=self.new_days, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        # Check updated days are True
        for day in self.days_list:
            self.assertEqual(getattr(updated_store, day), self.new_days[day])

    # Testing of the field type is addressed in the Store serializer tests

    # Testing for unknown fields is addressed in the Store serializer tests.

    def test_days_of_operation(self):
        expected_days = [
            day.capitalize() for day, value in self.initial_days.items() if value
        ]
        self.assertEqual(self.serializer.data["days_of_operation"], str(expected_days))

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            "id",
            "name",
            "owner_name",
            "manager_names",
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


class HoursSerializerTest(StoreBaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = HoursSerializer(instance=self.store)

    # Testing of the field type is addressed in the Store serializer tests
    # Testing unknown fields is addressed in the Store serializer tests.
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
                ("opening_time", "Time has wrong format"),
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
            serializer = HoursSerializer(self.store, data=test_data, partial=True)
            self.assertFalse(serializer.is_valid())
            # print(test_data, error_field, expected_error, serializer.errors)
            self.assertIn(expected_error, str(serializer.errors[error_field]))

        # Test valid case
        valid_cases = [
            {"closing_time": "17:00:00"},
            {"opening_time": "9:30", "closing_time": "9:45:30"},
        ]

        for valid_times in valid_cases:
            serializer = HoursSerializer(self.store, data=valid_times, partial=True)
            self.assertTrue(serializer.is_valid())

    def test_update_hours(self):
        new_hours = {"opening_time": "10:00:00", "closing_time": "20:00:00"}
        serializer = HoursSerializer(self.store, data=new_hours, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.opening_time, time(10, 0))
        self.assertEqual(updated_store.closing_time, time(20, 0))

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
            "owner_name",
            "manager_names",
            "opening_time",
            "closing_time",
            "days_of_operation",
        }
        self.assertEqual(set(data.keys()), expected_fields)


class ManagersSerializerTest(StoreBaseTestCase):
    def setUp(self):
        super().setUp()
        # I dont think this line is necessary either.
        # self.new_manager = User.objects.create_user(**MANAGER3_DATA)
        self.serializer = ManagersSerializer(instance=self.store)

    def test_initial_managers(self):
        self.assertEqual(self.store.manager_ids.count(), 1)

    def test_add_manager(self):
        old = self.store.manager_ids.count()
        self._create_user("manager", 2, MANAGER2_DATA)
        data = {"manager_ids": [self.manager2.id]}
        serializer = ManagersSerializer(self.store, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.manager_ids.count(), old + 1)
        self.assertIn(self.manager1, updated_store.manager_ids.all())
        self.assertIn(self.manager2, updated_store.manager_ids.all())

    def test_remove_manager(self):
        # Initial state verified by test_initial_managers
        data = {"manager_ids": [self.manager1.id]}
        serializer = ManagersSerializer(self.store, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.manager_ids.count(), 0)
        self.assertNotIn(self.manager1, updated_store.manager_ids.all())

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
            "owner_name",
            "manager_names",
            "manager_ids",
            "days_of_operation",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    # Testing of the field type is addressed in the Store serializer tests

    # Testing for unknown fields is addressed in the Store serializer tests.
