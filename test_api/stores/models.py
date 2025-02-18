from django.db import models


# Create your models here.
STATE_CHOICES = {
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


class Store(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="owned_stores"
    )
    managers = models.ManyToManyField(
        "users.CustomUser", related_name="managed_stores", blank=True
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2, choices=STATE_CHOICES.items())
    plz = models.CharField(max_length=5)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def location(self):
        return f"{self.address}, {self.city}, {STATE_CHOICES[self.state]}"

    # transfer ownership method?
