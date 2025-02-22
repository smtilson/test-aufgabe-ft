from stores.models import Store, DAYS_OF_WEEK
from django.contrib.auth import get_user_model
import random
from datetime import time, timedelta

User = get_user_model()


FIRST_NAMES = (
    "Emma",
    "Liam",
    "Olivia",
    "Noah",
    "Ava",
    "Oliver",
    "Isabella",
    "William",
    "Sophia",
    "James",
    "Mia",
    "Lucas",
)

LAST_NAMES = (
    "Schmidt",
    "Mueller",
    "Fischer",
    "Weber",
    "Meyer",
    "Wagner",
    "Becker",
    "Schulz",
    "Hoffmann",
    "Koch",
)

EMAIL_DOMAINS = (
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "proton.me",
    "example.com",
)

CITIES = (
    "Berlin",
    "Hamburg",
    "Munich",
    "Cologne",
    "Frankfurt",
    "Stuttgart",
    "Düsseldorf",
    "Leipzig",
    "Dortmund",
    "Essen",
)

STREET_NAMES = (
    "Hauptstraße",
    "Schulstraße",
    "Bahnhofstraße",
    "Gartenstraße",
    "Kirchstraße",
    "Bergstraße",
    "Waldstraße",
    "Ringstraße",
)

STREET_NUMBERS = tuple((str(i) for i in range(1, 201)))

PLZ_CODES = ("12345", "23456", "34567", "45678", "56789", "67890", "78901", "89012")

STORE_PREFIXES = (
    "Brot",
    "Back",
    "Gold",
    "Mehl",
    "Bäcker",
    "Brezel",
    "Kaffee",
    "Kuchen",
    "Zucker",
    "Konditorei",
)

STORE_MIDS = (
    "haus",
    "stube",
    "reich",
    "traum",
    "ecke",
    "zeit",
    "korb",
    "werk",
    "laden",
    "manufaktur",
)

STORE_SUFFIXES = (
    "Express",
    "Plus",
    "& Co",
    "GmbH",
    "Berlin",
    "Deluxe",
    "Premium",
    "Classic",
    "Original",
    "Tradition",
)

OPENING_TIMES = (
    "06:00:00",
    "06:30:00",
    "07:00:00",
    "07:30:00",
    "08:00:00",
    "08:30:00",
    "09:00:00",
    "09:30:00",
)

CLOSING_TIMES = (
    "17:00:00",
    "17:30:00",
    "18:00:00",
    "18:30:00",
    "19:00:00",
    "19:30:00",
    "20:00:00",
    "20:30:00",
    "21:00:00",
    "22:00:00",
)

DAYS = tuple((day for day in DAYS_OF_WEEK))

STATE = tuple((abbrv for abbrv in Store.STATES))

PASSWORD = "StRoNgPaSsWoRd123!"


def generate_user():
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(EMAIL_DOMAINS)}"
    return User.objects.create_user(
        email=email,
        password=PASSWORD,
        first_name=first_name,
        last_name=last_name,
    )


def store_owner():
    return generate_user()


def store_managers(num_managers):
    return [generate_user() for _ in range(num_managers)]


CITY_INCLUSION_PROBABILITY = 0.3  # 70% chance to include city
SUFFIX_INCLUSION_PROBABILITY = 0.3  # 30% chance to include suffix


def generate_store_name(city):
    prefix = random.choice(STORE_PREFIXES) + " "
    mid = random.choice(STORE_MIDS) + " "

    # Random decisions using fixed probabilities
    include_city = random.random() < CITY_INCLUSION_PROBABILITY
    include_suffix = random.random() < SUFFIX_INCLUSION_PROBABILITY
    suffix = random.choice(STORE_SUFFIXES) if include_suffix else ""
    city = ", " + city if include_city else ""

    return prefix + mid + suffix + city


def generate_store():
    city = random.choice(CITIES)
    address = random.choice(STREET_NAMES) + random.choice(STREET_NUMBERS)
    plz = random.choice(PLZ_CODES)
    opening = random.choice(OPENING_TIMES)
    closing = random.choice(CLOSING_TIMES)
    state = random.choice(STATE)

    name = generate_store_name(city)
    owner = store_owner()

    store = Store.objects.create(
        owner_id=owner,
        name=name,
        city=city,
        address=address,
        plz=plz,
        opening_time=time.fromisoformat(opening),
        closing_time=time.fromisoformat(closing),
        state_abbrv=state,
    )

    for manager in store_managers(random.randint(1, 4)):
        store.managers.add(manager)
    store.save()

    return store


def populate_database(num_stores, num_regular_users):
    # First create regular users
    regular_users = [generate_user() for _ in range(num_regular_users)]

    # Create stores with random owners and managers
    stores = [generate_store() for _ in range(num_stores)]
    for store in stores:
        for day in DAYS:
            setattr(store, day, random.choice([True, False]))

        setattr(store, "opening_time", random.choice(OPENING_TIMES))
        setattr(store, "closing_time", random.choice(CLOSING_TIMES))
        store.save()

    return regular_users, stores


def clear_database():
    Store.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    return "Database cleared except for superusers"
