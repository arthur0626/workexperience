from django.db import models
from django.contrib.auth.models import User

class UserSurvey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_location = models.CharField(max_length=100)
    budget = models.CharField(max_length=100)
    facilities = models.TextField()
    submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Survey"