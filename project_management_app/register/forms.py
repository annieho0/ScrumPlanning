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
    person = WorkingHour.objects.values('person').distinct()
    

    date = forms.ModelChoiceField(queryset=WorkingHour.objects.values('date').distinct())

    person = forms.ModelChoiceField(queryset=WorkingHour.objects.values('person').distinct(), to_field_name='name')

    class Meta:
        model = WorkingHour
        fields = [
            "date",
            "person",
        ]

