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
    open_days = models.ManyToManyField("Day", related_name="stores", blank=True)
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
        return [DAYS_OF_WEEK[day.day] for day in self.open_days.all()]

    # transfer ownership method?


DAYS_OF_WEEK = {
    "Mo": "Montag",
    "Di": "Dienstag",
    "Mi": "Mittwoch",
    "Do": "Donnerstag",
    "Fr": "Freitag",
    "Sa": "Samstag",
    "So": "Sonntag",
}


class Day(models.Model):
    day = models.CharField(max_length=2, choices=DAYS_OF_WEEK.items(), unique=True)

    @classmethod
    def initialize_days(cls):
        for day in DAYS_OF_WEEK.keys():
            Day.objects.get_or_create(day=day)
        return Day.objects.all()

    def __str__(self):
        return DAYS_OF_WEEK[self.day]
