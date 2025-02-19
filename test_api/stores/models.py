from django.db import models


# Create your models here.


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
        "users.CustomUser", on_delete=models.CASCADE, related_name="owned_stores"
    )
    managers = models.ManyToManyField(
        "users.CustomUser", related_name="managed_stores", blank=True
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state_abbrv = models.CharField(max_length=2, choices=STATES.items())
    plz = models.CharField(max_length=5)
    montag = models.BooleanField(default=False)
    dienstag = models.BooleanField(default=False)
    mittwoch = models.BooleanField(default=False)
    donnerstag = models.BooleanField(default=False)
    freitag = models.BooleanField(default=False)
    samstag = models.BooleanField(default=False)
    sonntag = models.BooleanField(default=False)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def location(self):
        return f"{self.address}, {self.city}, {self.state_abbrv}"

    @property
    def state(self):
        return self.STATE_CHOICES[self.state_abbrv]

    @property
    def days_open(self):
        return str([day.capitalize() for day in DAYS_OF_WEEK if getattr(self, day)])

    # transfer ownership method?


DAYS_OF_WEEK = [
    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",
]
