from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import time
from stores.models import Store
from stores.api.serializers import (
    StoreSerializer,
    DaysSerializer,
    HoursSerializer,
    ManagersSerializer,
)

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


class StoreSerializerTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = StoreSerializer(instance=self.store)

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
        serializer = StoreSerializer(data=new_store_data)
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

    def test_invalid_state_abbreviation(self):
        serialized_data = self.serializer.data
        serialized_data["state_abbrv"] = "XX"

        serializer = StoreSerializer(data=serialized_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("state_abbrv", serializer.errors)
        self.assertIn(
            "is not a valid choice.", str(serializer.errors["state_abbrv"][0])
        )

    def test_invalid_plz(self):
        serialized_data = self.serializer.data
        serialized_data["plz"] = "123ab"
        serializer = StoreSerializer(data=serialized_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("plz", serializer.errors)
        self.assertIn("only numbers", str(serializer.errors["plz"][0]))

        serialized_data["plz"] = "123456"
        serializer = StoreSerializer(data=serialized_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("plz", serializer.errors)
        self.assertIn("exactly 5 digits", str(serializer.errors["plz"][0]))

    def test_initial_days(self):
        for day in self.initial_days:
            self.assertEqual(getattr(self.store, day), self.initial_days[day])

    def test_optional_fields(self):
        required_data = {
            "name": "Test Store",
            "owner_id": self.owner.id,
            "address": "123 Test St",
            "city": "Test City",
            "state_abbrv": "BE",
        }
        serializer = StoreSerializer(data=required_data)
        self.assertTrue(serializer.is_valid())

    def test_required_fields(self):
        serializer = StoreSerializer(data={})
        self.assertFalse(serializer.is_valid())
        required_fields = {"name", "owner_id", "address", "city", "state_abbrv"}
        for field in required_fields:
            self.assertIn(field, serializer.errors)
        for field in serializer.errors:
            self.assertIn(field, required_fields)

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

    def test_add_new_manager(self):
        new_manager_data = {key: value + "1" for key, value in MANAGER_DATA.items()}
        new_manager = User.objects.create_user(**new_manager_data)

        update_data = {"manager_ids": [new_manager.id]}
        serializer = StoreSerializer(
            instance=self.store, data=update_data, partial=True
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
            instance=self.store, data=update_data, partial=True
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
        update_data = {"owner_id": new_owner.id}
        serializer = StoreSerializer(
            instance=self.store, data=update_data, partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()
        self.assertEqual(updated_store.owner_id, new_owner)

    def test_validate_time_range(self):
        invalid_data = {
            "name": "Test Store",
            "owner_id": self.owner.id,
            "address": "Test Address",
            "city": "Test City",
            "state_abbrv": "BE",
            "plz": "12345",
            "opening_time": "17:00:00",
            "closing_time": "09:00:00",
            "manager_ids": [self.manager.id],
        }
        serializer = StoreSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("closing_time", serializer.errors)


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

    def test_update_hours(self):
        new_hours = {"opening_time": "10:00:00", "closing_time": "20:00:00"}
        serializer = HoursSerializer(self.store, data=new_hours, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_store = serializer.save()

        self.assertEqual(updated_store.opening_time, time(10, 0))
        self.assertEqual(updated_store.closing_time, time(20, 0))
