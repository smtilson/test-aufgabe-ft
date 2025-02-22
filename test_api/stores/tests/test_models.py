from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import time
from stores.models import Store


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


class StoreModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(**OWNER_DATA)
        self.manager = User.objects.create_user(**MANAGER_DATA)
        self.store = Store.objects.create(owner_id=self.owner, **STORE_DATA)

    def test_store_creation(self):
        self.assertEqual(self.store.name, "Test Store")
        self.assertEqual(self.store.address, "123 Main St")
        self.assertEqual(self.store.city, "Test City")
        self.assertEqual(self.store.state_abbrv, "BE")
        self.assertEqual(self.store.plz, "12345")
        self.assertEqual(self.store.owner_id, self.owner)
        self.assertEqual(self.store.manager_ids.first(), None)
        self.assertEqual(self.store.opening_time, time(9, 0))
        self.assertEqual(self.store.closing_time, time(17, 0))

    def test_store_location_properties(self):
        self.assertEqual(self.store.location, "123 Main St, Test City, BE")
        self.assertEqual(self.store.state, "Berlin")

    def test_days_open_property(self):
        self.assertEqual(self.store.days_open, str([]))
        days = ["montag", "dienstag", "mittwoch"]
        for day in days:
            setattr(self.store, day, True)
        self.store.save()
        self.assertEqual(self.store.days_open, str([day.capitalize() for day in days]))

    # I don't think I need day_data property at all
    def test_day_data_property(self):
        self.store.dienstag = True
        self.store.freitag = True
        self.store.save()

        expected_data = {
            "montag": False,
            "dienstag": True,
            "mittwoch": False,
            "donnerstag": False,
            "freitag": True,
            "samstag": False,
            "sonntag": False,
        }
        self.assertEqual(self.store.day_data, expected_data)

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

        # Fetch fresh instance from database
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
        self.assertFalse(stored_store.montag)  # BooleanField
        self.assertEqual(stored_store.opening_time, time(9, 0))  # TimeField
        self.assertEqual(list(stored_store.manager_ids.all()), [])  # ManyToManyField

    def test_delete_store(self):
        store_id = self.store.id
        self.store.delete()
        self.assertEqual(Store.objects.filter(id=store_id).count(), 0)

    def test_manager_operations(self):
        # Create test managers
        manager1 = User.objects.create_user(
            email="manager1@test.com",
            password="testpass123",
            first_name="Manager",
            last_name="One",
        )
        manager2 = User.objects.create_user(
            email="manager2@test.com",
            password="testpass123",
            first_name="Manager",
            last_name="Two",
        )

        # Test adding managers
        self.store.manager_ids.add(manager1, manager2)
        self.assertEqual(self.store.manager_ids.count(), 2)
        self.assertIn(manager1, self.store.manager_ids.all())
        self.assertIn(manager2, self.store.manager_ids.all())

        # Test removing a manager
        self.store.manager_ids.remove(manager1)
        self.assertEqual(self.store.manager_ids.count(), 1)
        self.assertNotIn(manager1, self.store.manager_ids.all())
        self.assertIn(manager2, self.store.manager_ids.all())

        # Test clearing all managers
        self.store.manager_ids.clear()
        self.assertEqual(self.store.manager_ids.count(), 0)

    def test_owner_cascade_delete(self):
        store_id = self.store.id
        self.owner.delete()
        # Store should be deleted when owner is deleted due to CASCADE
        self.assertFalse(Store.objects.filter(id=store_id).exists())
