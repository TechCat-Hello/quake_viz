from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quakeapp_search_histories')
    keyword = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.keyword}"
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    min_magnitude = models.FloatField()
    max_magnitude = models.FloatField()
    prefecture = models.CharField(max_length=50)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.prefecture} - {self.start_year}~{self.end_year}"   