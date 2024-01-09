from django.db import models

class WeatherEntry(models.Model):
    layer_name = models.CharField(max_length=300, verbose_name="Layer Name")
    value = models.FloatField()
    latitude = models.FloatField(verbose_name="Latitude")
    longitude = models.FloatField(verbose_name="Longitude")
    date = models.DateTimeField(verbose_name="Date Recorded", auto_now_add=True)

    def __str__(self):
        return f"{self.latitude}, {self.longitude} - {self.layer_name} - {self.value}"
