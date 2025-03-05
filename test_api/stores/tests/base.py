from django.test import TestCase
from django.urls import clear_url_caches
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from unittest.mock import Mock

from users.models import CustomUser
from stores.models import Store
from .data import *


class AbstractBaseTestCase(object):
    """Common functionality shared across all test types"""

    def _create_user(self, role, number, data):
        """Creates a single user and adds to users dictionary."""
        user = CustomUser.objects.create_user(**data)
        setattr(self, f"{role}{number}", user)
        return user

    def _setup_common_data(self):
        """Setup common test data structures"""
        self.days_list = DAYS_LIST
        self.initial_days = DEFAULT_DAYS.copy()
        self.times = DEFAULT_TIMES.copy()


class StoreBaseTestCase(TestCase, AbstractBaseTestCase):
    """Base test case for Store model tests"""

    @classmethod
    def setUpClass(cls):
        print(f"\nInitializing test class: {cls.__name__}")
        TestCase.setUpClass()

    def setUp(self):
        """Create common test data: users, store, and related objects"""
        TestCase.setUp(self)
        self._create_users()
        self._setup_common_data()
        self._create_base_store()
        self.store.manager_ids.add(self.manager1)

    def _create_users(self):
        """Create the standard test users needed for model tests"""
        self._create_user("owner", 1, OWNER1_DATA)
        self._create_user("manager", 1, MANAGER1_DATA)

    def _create_base_store(self):
        """Create the primary test store"""
        self.store = Store.objects.create(
            owner=self.owner1, **STORE1_DATA, **self.initial_days, **self.times
        )


class APIBaseTestCase(APITestCase, AbstractBaseTestCase):
    """Base test case for API tests"""

    @classmethod
    def setUpClass(cls):
        print(f"\nInitializing test class: {cls.__name__}")
        APITestCase.setUpClass()

    def setUp(self):
        """Create common test data: users, stores, auth tokens"""
        # should self be removed?
        APITestCase.setUp(self)
        clear_url_caches()

        # Create users
        self._setup_superuser()
        self._create_users()

        # Setup common data
        self._setup_common_data()

        # Create stores
        self._create_multiple_stores()

        # Add managers to stores
        self.store1.manager_ids.add(self.manager1)
        self.store2.manager_ids.add(self.manager2)

        # Create and setup authentication, and context requests
        self._setup_authentication()
        self._setup_context_requests()

    def _create_users(self):
        """Create all users needed for API tests"""
        self._create_user("owner", 1, OWNER1_DATA)
        self._create_user("owner", 2, OWNER2_DATA)
        self._create_user("manager", 1, MANAGER1_DATA)
        self._create_user("manager", 2, MANAGER2_DATA)

    def _create_multiple_stores(self):
        """Create the multiple stores needed for API tests"""
        self.store1 = Store.objects.create(
            owner=self.owner1, **STORE1_DATA, **self.initial_days, **self.times
        )
        self.store2 = Store.objects.create(
            owner=self.owner1, **STORE2_DATA, **self.initial_days, **self.times
        )
        self.store3 = Store.objects.create(
            owner=self.owner2, **STORE3_DATA, **self.initial_days, **self.times
        )

    def _setup_authentication(self):
        """Setup authentication tokens and client defaults"""

        # Set up client with default auth and format
        token = self.owner1.auth_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.client.defaults["HTTP_ACCEPT"] = "application/json"
        self.client.defaults["format"] = "json"

    def _setup_superuser(self):
        """Create superuser if not created already"""
        self.super_user, created = CustomUser.objects.get_or_create(
            email="superuser@super.user",
            defaults={"password": "superuser", "is_superuser": True, "is_staff": True},
        )
        if created:
            # WORKAROUND: Explicitly setting auth_token attribute to bypass property
            # method issues with superusers in test environment
            self.super_user.auth_token, _ = Token.objects.get_or_create(
                user=self.super_user
            )
            self.super_user.set_password("superuser")
            self.super_user.save()

    def _setup_context_requests(self):
        """Create mock request contexts for serializer testing"""
        for method in {"PATCH", "POST", "PUT", "DELETE"}:
            method_request = Mock()
            method_request.method = method
            method_request.user = self.owner1
            setattr(self, f"context_{method}", {"request": method_request})

    def switch_to(self, user):
        """Switch client auth to specified user

        Args:
            user_key: String key identifying the user (e.g., 'owner1', 'manager1', 'superuser')

        Raises:
            ValueError: If user_key is not found in the users dictionary
        """
        user.refresh_from_db()
        token = user.auth_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        return self  # Allow method chaining

    # URL filtering helper methods
    def url_comparison(self, field, value, comparison):
        return f"{field}_{comparison}={value}"

    def django_comparison(self, field, comparison):
        return f"{field}__{comparison}"

    def django_id_query(self, field, specifier):
        return f"{field}_ids__{specifier}"

    def url_id_query(self, field, specifier):
        return f"{field}_{specifier}"
