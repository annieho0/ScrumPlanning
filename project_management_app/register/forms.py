from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import CustomizedUser, WorkingHour
from django.db import models

class RegisterFrom(UserCreationForm):
    """
    This class is used to create a form for user registration.
    """
    email = forms.EmailField()
    class Meta:
        model = CustomizedUser
        constraints = [models.UniqueConstraint(fields='email', name='unique_email')]
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class CreateHourGraphForm(forms.ModelForm):
    date = forms.ChoiceField(choices=WorkingHour.objects.values('date').distinct())
    person = forms.ChoiceField(choices=WorkingHour.objects.values('person').distinct())

    class Meta:
        model = WorkingHour
        fields = [
            "date",
            "person"
        ]