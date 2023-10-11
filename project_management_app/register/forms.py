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
    """
    This class is used to create a form for drawing the graphs
    """
    person = WorkingHour.objects.values('person').distinct()
    person_choice = CustomizedUser.objects.filter(id__in=person)
    person = forms.ModelChoiceField(queryset=person_choice, label="Select 1 person")

    date_choices = WorkingHour.objects.values_list('date').distinct()
    choices = [(date[0], date[0].strftime('%Y-%m-%d')) for date in date_choices]
    choices.insert(0, (None, "---------"))

    date = forms.ChoiceField(
        choices=choices,
        label="Select 1 date for the whole team",
    )
    # date = forms.ModelChoiceField(queryset=WorkingHour.objects.values('date').distinct())

    class Meta:
        model = WorkingHour
        fields = [
            "date",
            "person",
        ]

