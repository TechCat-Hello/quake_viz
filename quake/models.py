from django.db import models
from django.contrib.auth.models import User

class Earthquake(models.Model):
    date = models.DateField()
    magnitude = models.FloatField()
    location = models.CharField(max_length=255)

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='histories')
    searched_at = models.DateTimeField(auto_now_add=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    min_magnitude = models.FloatField()
    max_magnitude = models.FloatField()
    prefecture = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.user.username} - {self.searched_at.strftime("%Y-%m-%d %H:%M")}'

