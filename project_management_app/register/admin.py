from django.contrib import admin
from .models import CustomizedUser, WorkingHour, ScrumRole
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomizedUser)
class CustomizedUserAdmin(UserAdmin):
    """
    Admin configuration for the CustomizedUser model.

    This class extends the UserAdmin class provided by Django's admin site.
    It customizes the display, filtering, search, ordering, and fieldsets for the CustomizedUser model.

    Attributes:
        list_display (tuple): The fields to display in the list view of the admin site.
        list_filter (tuple): The fields to use for filtering on the right sidebar in the list view.
        search_fields (tuple): The fields to use for searching in the search bar in the list view.
        ordering (tuple): The default ordering of the list view.
        fieldsets (tuple): The grouping of fields in the form view of the admin site.
    """

    # Displayed fields in the list view
    list_display = (
        'username','first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'scrum_role')

    # Fields used for filtering on the right sidebar in the list view
    list_filter = ('is_superuser', 'is_staff', 'is_active', 'scrum_role')

    # Fields used for searching in the search bar in the list view
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Default ordering of the list view
    ordering = ('username',)

    # Grouping of fields in the form view
    fieldsets = (
        ('Login Details', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Active and Roles', {
            'fields': ('is_active', 'scrum_role')
        }),
        ('Permissions', {
            'fields': ('is_admin', 'is_superuser', 'is_staff')
        }),
        ('History', {
            'fields': ('date_joined', 'last_login')
        })
    )



@admin.register(WorkingHour)
class WorkingHoursAdmin(admin.ModelAdmin):
    pass


@admin.register(ScrumRole)
class ScrumRoleAdmin(admin.ModelAdmin):
    pass