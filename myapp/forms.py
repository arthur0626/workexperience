from django import forms
from .models import ProtectedProfile, SelfProfile

class ProtectedProfileForm(forms.ModelForm):
    class Meta:
        model = ProtectedProfile
        fields = ['name', 'age', 'sex', 'guardian', 'preferred_location', 'budget', 'preferred_services', 'health_conditions', 'additional_info']

class SelfProfileForm(forms.ModelForm):
    class Meta:
        model = SelfProfile
        fields = ['kakao_id', 'name', 'scrapped', 'recent', 'reviews']
