from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import CustomizedUser
from django.db import models
class RegisterFrom(UserCreationForm):

    class Meta:
        model = CustomizedUser
        constraints = [models.UniqueConstraint(fields='email', name='unique_email')]
        fields = ["email", "password1", "password2", 
                  "first_name", "last_name"]
