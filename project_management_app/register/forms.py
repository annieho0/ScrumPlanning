from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import CustomizedUser
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
