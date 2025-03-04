from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import time
from stores.models import Store
from .data import *
from .base import StoreBaseTestCase


User = get_user_model()


class StoreModelTest(StoreBaseTestCase):

    def setUp(self):
        super().setUp()
        self.owner = self.owner1
        self.manager = self.manager1

    # Creation Tests
    def test_store_creation(self):
        store = Store.objects.create(
            **STORE2_DATA, owner_id=self.owner, **self.initial_days, **self.times
        )

        store.refresh_from_db()

        self.assertEqual(store.name, "Test Store1")
        self.assertEqual(store.address, "123 Main St1")
        self.assertEqual(store.city, "Test City1")
        self.assertEqual(store.state_abbrv, "BE")
        self.assertEqual(store.plz, "12345")
        self.assertEqual(store.owner_id, self.owner)
        self.assertEqual(store.manager_ids.first(), None)
        self.assertEqual(store.opening_time, time(7, 0))
        self.assertEqual(store.closing_time, time(17, 0))

    # Property Tests
    def test_store_location_properties(self):
        self.assertEqual(self.store.location, "123 Main St, Test City, BE")
        self.assertEqual(self.store.state, "Berlin")

    def test_days_open_property(self):
        days = ["montag", "dienstag", "mittwoch"]
        self.assertEqual(self.store.days_open, str([day.capitalize() for day in days]))
        for day in days:
            setattr(self.store, day, False)
        self.store.save()
        self.assertEqual(self.store.days_open, str([]))

    # Validation Tests
    def test_invalid_state_abbreviation(self):
        with self.assertRaises(ValidationError) as e:
            invalid_store = Store(
                name="Invalid Store",
                owner_id=self.owner,
                address="Test Street 1",
                city="Test City",
                state_abbrv="XX",  # Invalid state
                plz="12345",
            )
            invalid_store.full_clean()

        error_dict = e.exception.message_dict
        self.assertIn("state_abbrv", error_dict)
        self.assertEqual(
            error_dict["state_abbrv"][0], "Value 'XX' is not a valid choice."
        )

    def test_missing_fields(self):
        with self.assertRaises(ValidationError) as e:
            invalid_store = Store(
                name="",  # Empty name
                owner_id=self.owner,
                address="",  # Empty address
                city="",  # Empty city
                state_abbrv="BE",
                plz="123456",  # Too long
            )
            invalid_store.full_clean()

        error_dict = e.exception.message_dict
        self.assertIn("name", error_dict)
        self.assertIn("address", error_dict)
        self.assertIn("city", error_dict)
        self.assertIn("plz", error_dict)

    # RUD Tests
    def test_update_all_store_fields(self):
        new_owner = User.objects.create_user(
            email="newowner@test.com",
            password="testpass123",
            first_name="New",
            last_name="Owner",
        )

        # Update fields, testing one of each type
        self.store.name = "Completely Updated Store"  # CharField
        self.store.owner_id = new_owner  # ForeignKey
        self.store.state_abbrv = "HH"  # CharField with choices
        self.store.montag = True  # BooleanField
        self.store.opening_time = time(8, 30)  # TimeField
        self.store.save()

        updated_store = Store.objects.get(id=self.store.id)

        # Verify updates by field type
        self.assertEqual(updated_store.name, "Completely Updated Store")
        self.assertEqual(updated_store.owner_id, new_owner)
        self.assertEqual(updated_store.state_abbrv, "HH")
        self.assertTrue(updated_store.montag)
        self.assertEqual(updated_store.opening_time, time(8, 30))

    def test_read_store(self):
        stored_store = Store.objects.get(id=self.store.id)

        # Test one field of each type
        self.assertEqual(stored_store.name, self.store.name)  # CharField
        self.assertEqual(stored_store.owner_id, self.owner)  # ForeignKey
        self.assertEqual(stored_store.state_abbrv, "BE")  # CharField with choices
        self.assertTrue(stored_store.montag)  # BooleanField
        self.assertEqual(stored_store.opening_time, time(7, 0))  # TimeField
        self.assertEqual(stored_store.manager_ids.count(), 1)  # ManyToManyField

    def test_delete_store(self):
        store_id = self.store.id
        self.store.delete()
        self.assertEqual(Store.objects.filter(id=store_id).count(), 0)

    # Manager relationship Tests
    def test_manager_operations(self):
        # Create test managers
        manager2 = User.objects.create_user(**MANAGER2_DATA)
        manager3 = User.objects.create_user(**MANAGER3_DATA)

        # Test adding managers
        old = self.store.manager_ids.count()
        self.store.manager_ids.add(manager2, manager3)
        self.assertEqual(self.store.manager_ids.count(), old + 2)
        self.assertIn(self.manager, self.store.manager_ids.all())
        self.assertIn(manager2, self.store.manager_ids.all())
        self.assertIn(manager3, self.store.manager_ids.all())

        # Test removing a manager
        self.store.refresh_from_db()
        current = self.store.manager_ids.count()
        self.store.manager_ids.remove(manager2)
        self.assertEqual(self.store.manager_ids.count(), current - 1)
        self.assertNotIn(manager2, self.store.manager_ids.all())
        self.assertIn(manager3, self.store.manager_ids.all())

        # Test clearing all managers
        self.store.manager_ids.clear()
        self.assertEqual(self.store.manager_ids.count(), 0)

    # Cascade deletion tests
    def test_owner_cascade_delete(self):
        store_id = self.store.id
        self.owner.delete()
        # Store should be deleted when owner is deleted due to CASCADE
        self.assertFalse(Store.objects.filter(id=store_id).exists())
