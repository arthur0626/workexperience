from django import forms
from .models import ProtectedProfile, SelfProfile

class ProtectedProfileForm(forms.ModelForm):
    class Meta:
        model = ProtectedProfile
        fields = ['name', 'age', 'sex', 'guardian', 'address', 'address_detail', 'budget_min', 'budget_max', 'preferred_services', 'health_conditions', 'additional_info']

class SelfProfileForm(forms.ModelForm):
    class Meta:
        model = SelfProfile
        fields = ['kakao_id', 'name', 'scrapped', 'recent', 'reviews']

class LocationForm(forms.ModelForm):
    class Meta:
        model = ProtectedProfile
        fields = ['address'] 