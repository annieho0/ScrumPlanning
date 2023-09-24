from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from project_task.models import Task
# Create your models here.

# class HoursWorked()



class CustomizedUser(AbstractBaseUser):
    email = models.EmailField(max_length=200, unique=True)
    # hours_worked is an integer field for now

    is_admin = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'email']



class WorkingHour(models.Model):
    task = models.ForeignKey('project_task.Task', on_delete=models.CASCADE, blank=True, null=True)
    person = models.ForeignKey('CustomizedUser', on_delete=models.CASCADE)
    date = models.DateField()
    hour = models.DurationField()