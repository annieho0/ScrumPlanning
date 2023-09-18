from django.db import models
from django.contrib.auth.models import AbstractBaseUser
# Create your models here.

# class HoursWorked():



class CustomizedUser(AbstractBaseUser):
    email = models.EmailField(max_length=200, unique=True)
    # hours_worked is an integer field for now
    hours_worked = models.IntegerField(default=0)

    is_admin = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'email']

