from django.db import models
from users.models import CustomUser


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
