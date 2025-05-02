from django.db import models
from django.contrib.auth.models import User

class Earthquake(models.Model):
    date = models.DateField()
    magnitude = models.FloatField()
    location = models.CharField(max_length=255)
    # 他にも深さ、緯度経度など

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quake_search_histories')
    keyword = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.keyword}"

