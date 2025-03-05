from django.db import models
from users.models import CustomUser
from django.core.exceptions import ValidationError

# Create your models here.

DAYS_OF_WEEK = [
    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",
]


class Store(models.Model):
    STATES = {
        "BW": "Baden-Württemberg",
        "BY": "Bayern",
        "BE": "Berlin",
        "BB": "Brandenburg",
        "HB": "Bremen",
        "HH": "Hamburg",
        "HE": "Hessen",
        "MV": "Mecklenburg-Vorpommern",
        "NI": "Niedersachsen",
        "NW": "Nordrhein-Westfalen",
        "RP": "Rheinland-Pfalz",
        "SL": "Saarland",
        "SN": "Sachsen",
        "ST": "Sachsen-Anhalt",
        "SH": "Schleswig-Holstein",
        "TH": "Thüringen",
    }

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="owned_stores"
    )
    manager_ids = models.ManyToManyField(
        CustomUser, related_name="managed_stores", blank=True
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state_abbrv = models.CharField(max_length=2, choices=STATES.items())
    plz = models.CharField(max_length=5, blank=True)
    montag = models.BooleanField(default=False)
    dienstag = models.BooleanField(default=False)
    mittwoch = models.BooleanField(default=False)
    donnerstag = models.BooleanField(default=False)
    freitag = models.BooleanField(default=False)
    samstag = models.BooleanField(default=False)
    sonntag = models.BooleanField(default=False)
    opening_time = models.TimeField(default="07:00:00")
    closing_time = models.TimeField(default="17:00:00")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    @property
    def location(self):
        return f"{self.address}, {self.city}, {self.state_abbrv}"

    @property
    def state(self):
        return self.STATES[self.state_abbrv]

    @property
    def days_open(self):
        return str([day.capitalize() for day in DAYS_OF_WEEK if getattr(self, day)])


class StoreHours(models.Model):
    DAYS_OF_WEEK_DICT = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    DAYS_OF_WEEK = [(key, value) for key, value in DAYS_OF_WEEK_DICT.items()]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="hours")
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    opening_time = models.TimeField(default="07:00:00")
    closing_time = models.TimeField(default="17:00:00")

    class Meta:
        ordering = ["store", "day"]
        unique_together = ["store", "day"]

    def __str__(self):
        return f"{self.store.name} - {self.DAYS_OF_WEEK[self.day]}: {self.opening_time} - {self.closing_time}"
