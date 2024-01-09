from django.db import models

class WeatherEntry(models.Model):
    layer_name = models.CharField(max_length=300, verbose_name="Layer Name")
    value = models.FloatField()
    location = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.location} - {self.layer_name} - {self.value}"