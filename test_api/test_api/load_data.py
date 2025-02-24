from stores.models import Store, DAYS_OF_WEEK
from django.contrib.auth import get_user_model
import random
from time import time

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
    "Charlotte",
    "Henry",
    "Amelia",
    "Alexander",
    "Luna",
    "Benjamin",
    "Harper",
    "Sebastian",
    "Ella",
    "Theodore",
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
    "Richter",
    "Klein",
    "Wolf",
    "Schroeder",
    "Neumann",
    "Schwarz",
    "Zimmermann",
    "Braun",
    "Krause",
    "Schmitz",
)

EMAIL_DOMAINS = (
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "proton.me",
    "example.com",
    "icloud.com",
    "mail.com",
    "web.de",
    "gmx.de",
    "t-online.de",
    "posteo.de",
    "mailbox.org",
    "fastmail.com",
    "zoho.com",
    "aol.com",
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


def get_used_emails():
    return set(User.objects.values_list("email", flat=True))


def generate_user():
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    invalid_emails = get_used_emails()
    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(EMAIL_DOMAINS)}"
    while email in invalid_emails:
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = (
            f"{first_name.lower()}.{last_name.lower()}@{random.choice(EMAIL_DOMAINS)}"
        )
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


def generate_store(owner):
    city = random.choice(CITIES)
    name = generate_store_name(city)
    number_first = random.choice([True, False])
    if number_first:
        address = random.choice(STREET_NUMBERS) + " " + random.choice(STREET_NAMES)
    else:
        address = random.choice(STREET_NAMES)
    store = Store.objects.create(
        owner_id=owner,
        name=name,
        city=city,
        address=address,
        plz=random.choice(PLZ_CODES),
        opening_time=random.choice(OPENING_TIMES),
        closing_time=random.choice(CLOSING_TIMES),
        state_abbrv=random.choice(STATE),
    )

    number_of_days = 0
    while number_of_days < 3:
        for day in DAYS:
            setattr(store, day, False)
            choice = random.choice([True, False])
            if choice:
                number_of_days += 1
            setattr(store, day, choice)
    store.save()
    return store


def generate_store_old():
    city = random.choice(CITIES)
    name = generate_store_name(city)
    number_first = random.choice([True, False])
    if number_first:
        address = random.choice(STREET_NUMBERS) + " " + random.choice(STREET_NAMES)
    else:
        address = random.choice(STREET_NAMES)
    store = Store.objects.create(
        owner_id=store_owner(),
        name=name,
        city=city,
        address=address,
        plz=random.choice(PLZ_CODES),
        opening_time=random.choice(OPENING_TIMES),
        closing_time=random.choice(CLOSING_TIMES),
        state_abbrv=random.choice(STATE),
    )

    for manager in store_managers(random.randint(1, 4)):
        store.manager_ids.add(manager)
    number_of_days = 0
    while number_of_days < 3:
        for day in DAYS:
            setattr(store, day, False)
            choice = random.choice([True, False])
            if choice:
                number_of_days += 1
            setattr(store, day, choice)

    store.save()
    return store


def bulk_populate(num_stores, num_users, big_owner=None):
    absolute_start_time = time()
    # First create regular users
    users_start_time = time()
    if num_users <= num_stores:
        raise ValueError("Number of users must be greater than number of stores")
    users = [generate_user() for _ in range(num_users)]
    users_end_time = time()
    stores_start_time = time()
    stores = []
    store_count = num_stores
    while store_count > 0:
        index = random.randint(0, len(users) - 1)
        if big_owner:
            store = generate_store(big_owner)
        else:
            store = generate_store(users.pop(index))
        stores.append(store)
        store_count -= 1
    stores_end_time = time()
    manager_assignment_start_time = time()
    for store in stores:
        for _ in range(random.randint(1, 4)):
            store.manager_ids.add(random.choice(users))
            store.save()
    manager_assignment_end_time = time()
    total_manager_assignment_time = (
        manager_assignment_end_time - manager_assignment_start_time
    )
    total_execution_time = time() - absolute_start_time
    total_users_time = users_end_time - users_start_time
    total_stores_time = stores_end_time - stores_start_time
    # print(f"Total users: {num_users}\nCreated in {total_users_time:.2f} seconds")
    #  print(f"Total stores: {num_stores}\nCreated in {total_stores_time:.2f} seconds")
    #   (f"Total manager assignment time: {total_manager_assignment_time:.2f} seconds")
    #    print(f"Total execution time: {total_execution_time:.2f} seconds")
    return stores, users


def populate_database(num_stores, num_regular_users):
    absolute_start_time = time()
    # First create regular users
    users_start_time = time()
    for _ in range(num_regular_users):
        generate_user()
    users_end_time = time()
    # Create stores with random owners and managers
    stores_start_time = time()
    for _ in range(num_stores):
        generate_store_old()
    stores_end_time = time()
    user_execution_time = users_end_time - users_start_time
    store_execution_time = stores_end_time - stores_start_time
    total_execution_time = time() - absolute_start_time
    num_users = User.objects.count()
    num_stores = Store.objects.count()
    print(f"Total users: {num_users}\nCreated in {user_execution_time:.2f} seconds")
    print(f"Total stores: {num_stores}\nCreated in {store_execution_time:.2f} seconds")
    print(f"Total execution time: {total_execution_time:.2f} seconds")


def clear_database():
    # Initial counts
    absolute_start_time = time()
    initial_users = User.objects.count()
    initial_superusers = User.objects.filter(is_superuser=True).count()
    initial_stores = Store.objects.count()

    print(f"Initial database state:")
    print(f"Total users: {initial_users}")
    print(f"Superusers: {initial_superusers}")
    print(f"Stores: {initial_stores}")

    # Get users to delete
    users_to_delete = User.objects.filter(is_superuser=False)
    for superuser in User.objects.filter(is_superuser=True):
        if superuser.email in set(users_to_delete.values_list("email", flat=True)):
            users_to_delete = users_to_delete.exclude(email=superuser.email)
    deletion_count = users_to_delete.count()
    print(f"\nDeleting {deletion_count} users and {initial_stores} stores")

    # Perform deletion
    stores_start_time = time()
    Store.objects.all().delete()
    stores_end_time = time()
    users_start_time = time()
    users_to_delete.delete()
    users_end_time = time()
    # Final counts
    final_users = User.objects.count()
    final_stores = Store.objects.count()
    total_execution_time = time() - absolute_start_time
    user_execution_time = users_end_time - users_start_time
    store_execution_time = stores_end_time - stores_start_time
    print(f"\nFinal database state:")
    print(
        f"Remaining users: {final_users}\n"
        f"Deleted {initial_users - final_users} users "
        f"in {user_execution_time:.2f} seconds."
    )
    print(
        f"Remaining stores: {final_stores}"
        f"Deleted {initial_stores - final_stores} stores "
        f"in {store_execution_time:.2f} seconds."
    )
    print(
        f"Deleted {initial_stores + initial_users - final_stores - final_users} "
        f"records in {total_execution_time:.2f} seconds"
    )

    print("Database cleared successfully")
