from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth import get_user_model

User = get_user_model()

# Test data constants
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
MANAGER3_DATA = {key: value + "1" for key, value in MANAGER2_DATA.items()}

STORE1_DATA = {
    "name": "Test Store",
    "address": "123 Main St",
    "city": "Test City",
    "state_abbrv": "BE",
    "plz": "12345",
}

STORE2_DATA = {key: value + "1" for key, value in STORE1_DATA.items()}
STORE3_DATA = {key: value + "1" for key, value in STORE2_DATA.items()}

# Fix PLZ and state_abbrv in store data
for key in {"plz", "state_abbrv"}:
    STORE2_DATA[key] = STORE1_DATA[key]
    STORE3_DATA[key] = STORE1_DATA[key]

DEFAULT_TIMES = {
    "opening_time": "07:00:00",
    "closing_time": "17:00:00",
}

DEFAULT_DAYS = {
    "montag": True,
    "dienstag": True,
    "mittwoch": True,
    "donnerstag": False,
    "freitag": False,
    "samstag": False,
    "sonntag": False,
}

DAYS_LIST = [
    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",
]
