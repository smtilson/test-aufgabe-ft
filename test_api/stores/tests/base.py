from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import clear_url_caches
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from unittest.mock import Mock

from stores.models import Store
from .data import *

User = get_user_model()

class AbstractBaseTestCase(object):
    """Common functionality shared across all test types"""
    
    @classmethod
    def setUpClass(cls):
        print(f"\nInitializing test class: {cls.__name__}")
    
    def _create_user(self, role, number, data):
        """Creates a single user and adds to users dictionary."""
        user = User.objects.create_user(**data)
        setattr(self, f"{role}{number}", user)
        
        # Create users dictionary if it doesn't exist
        if not hasattr(self, "users"):
            self.users = {}
            
        self.users[f"{role}{number}"] = user
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
        TestCase.setUpClass()
        AbstractBaseTestCase.setUpClass()
    
    def setUp(self):
        """Create common test data: users, store, and related objects"""
        TestCase.setUp(self)
        self._create_users()
        self._setup_common_data()
        self._create_base_store()
    
    def _create_users(self):
        """Create the standard test users needed for model tests"""
        self._create_user("owner", 1, OWNER1_DATA)
        self._create_user("manager", 1, MANAGER1_DATA)
    
    def _create_base_store(self):
        """Create the primary test store"""
        self.store = Store.objects.create(
            owner_id=self.owner1, 
            **STORE1_DATA, 
            **self.initial_days, 
            **self.times
        )


class APIBaseTestCase(APITestCase, AbstractBaseTestCase):
    """Base test case for API tests"""
    
    @classmethod
    def setUpClass(cls):
        APITestCase.setUpClass()
        AbstractBaseTestCase.setUpClass()
    
    def setUp(self):
        """Create common test data: users, stores, auth tokens"""
        # should self be removed?
        APITestCase.setUp(self)
        clear_url_caches()
        
        # Create users
        self._create_users()
        
        # Setup common data
        self._setup_common_data()
        
        # Create stores
        self._create_multiple_stores()
        
        # Add managers to stores
        self.store1.manager_ids.add(self.manager1)
        self.store2.manager_ids.add(self.manager2)
        
        # Create and setup authentication
        self._setup_authentication()
        
        # Setup admin/superuser if needed
        self._setup_superuser()
    
    def _create_users(self):
        """Create all users needed for API tests"""
        self._create_user("owner", 1, OWNER1_DATA)
        self._create_user("owner", 2, OWNER2_DATA)
        self._create_user("manager", 1, MANAGER1_DATA)
        self._create_user("manager", 2, MANAGER2_DATA)
    
    def _create_multiple_stores(self):
        """Create the multiple stores needed for API tests"""
        self.store1 = Store.objects.create(
            owner_id=self.owner1, **STORE1_DATA, **self.initial_days, **self.times
        )
        self.store2 = Store.objects.create(
            owner_id=self.owner1, **STORE2_DATA, **self.initial_days, **self.times
        )
        self.store3 = Store.objects.create(
            owner_id=self.owner2, **STORE3_DATA, **self.initial_days, **self.times
        )
        
    
    def _setup_authentication(self):
        """Setup authentication tokens and client defaults"""
        # Store users in dictionary for switch_to method
        self.users = {
            'owner1': self.owner1,
            'owner2': self.owner2,
            'manager1': self.manager1,
            'manager2': self.manager2
        }
        
        # Set up client with default auth and format
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner1.auth_token.key}")
        self.client.defaults["HTTP_ACCEPT"] = "application/json"
        self.client.defaults["format"] = "json"
    
    def _setup_superuser(self):
        """Create superuser if not created already"""
        self.super_user, created = User.objects.get_or_create(
            email="superuser@super.user",
            defaults={
                "password": "superuser",
                "is_superuser": True,
                "is_staff": True
            }
        )
        if created:
            self.super_user.set_password("superuser")
            self.super_user.save()
        
        # Add superuser to the users dictionary
        self.users['superuser'] = self.super_user
    
    def switch_to(self, user_key):
        """Switch client auth to specified user
        
        Args:
            user_key: String key identifying the user (e.g., 'owner1', 'manager1', 'superuser')
        
        Raises:
            ValueError: If user_key is not found in the users dictionary
        """
        if user_key not in self.users:
            raise ValueError(f"Unknown user key: {user_key}. Available keys: {list(self.users.keys())}")
        
        token = self.users[user_key].auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        return self  # Allow method chaining
    
    def setup_context_requests(self):
        """Create mock request contexts for serializer testing"""
        for method in {"PATCH", "POST", "PUT", "DELETE"}:
            method_request = Mock()
            method_request.method = method
            method_request.user = self.owner1
            setattr(self, f"context_{method}", {"request": method_request})
    
    # URL filtering helper methods
    def url_comparison(self, field, value, comparison):
        return f"{field}_{comparison}={value}"
    
    def django_comparison(self, field, comparison):
        return f"{field}__{comparison}"
    
    def django_id_query(self, field, specifier):
        return f"{field}_ids__{specifier}"
    
    def url_id_query(self, field, specifier):
        return f"{field}_{specifier}"