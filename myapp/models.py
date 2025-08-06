from django.db import models
from django.contrib.auth.models import User

class ProtectedProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='protected_profile') 
    name = models.CharField(null=True, max_length=100)
    age = models.PositiveIntegerField(null=True)
    sex = models.CharField(null=True, max_length=10)
    guardian = models.BooleanField(default=False)
    preferred_location = models.CharField(max_length=100)
    budget = models.IntegerField()
    preferred_services = models.TextField(blank=True)
    health_conditions = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (피보호자)"

class SelfProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='self_profile')
    kakao_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    scrapped = models.BooleanField(default=False)
    recent = models.BooleanField(default=False)
    reviews = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (자신)"
