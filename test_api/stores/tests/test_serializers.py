from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import time
from stores.models import Store
from stores.api.serializers import StoreSerializer

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
    "opening_time": time(9, 0),
    "closing_time": time(17, 0),
}

User = get_user_model()


class StoreSerializerTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(**OWNER_DATA)
        self.manager = User.objects.create_user(**MANAGER_DATA)
        self.store = Store.objects.create(owner_id=self.owner, **STORE_DATA)
        self.store.manager_ids.add(self.manager)
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
            "open_days",
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

    def test_open_days_field(self):
        self.store.montag = True
        self.store.mittwoch = True
        self.store.save()
        serializer = StoreSerializer(instance=self.store)
        self.assertEqual(serializer.data["open_days"], str(["Montag", "Mittwoch"]))

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


"""
    def test_invalid_time_range(self):
        invalid_data = {
            **STORE_DATA,
            "opening_time": time(17, 0),
            "closing_time": time(9, 0),
            "owner_id": self.owner.id,
        }
        serializer = StoreSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("closing_time", serializer.errors)
        self.assertEqual(
            serializer.errors["closing_time"][0],
            "Closing time must be later than opening time",
        )
"""
