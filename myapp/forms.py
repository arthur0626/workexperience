from django import forms
from .models import UserSurvey

class UserSurveyForm(forms.ModelForm):
    class Meta:
        model = UserSurvey
        fields = ['preferred_location', 'budget', 'facilities']
