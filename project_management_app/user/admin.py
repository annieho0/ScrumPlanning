from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # Helper Class for creating user admin pages

from .forms import CustomUserCreationForm  #, CustomUserChangeForm
from .models import CustomizedUser

@admin.register(CustomizedUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    model = CustomizedUser

    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    search_fields = ('email', 'username',)
    readonly_fields = ('date_joined', 'last_login',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


# admin.site.register(custom_user_model, CustomUserAdmin)