from django.db import models

class Earthquake(models.Model):
    date = models.DateField()
    magnitude = models.FloatField()
    location = models.CharField(max_length=255)
    # 他にも深さ、緯度経度など

