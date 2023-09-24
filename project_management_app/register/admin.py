from django.contrib import admin
from .models import CustomizedUser, WorkingHour
# Register your models here.

@admin.register(CustomizedUser)
class CustomizedUserAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkingHour)
class WorkingHoursAdmin(admin.ModelAdmin):
    pass