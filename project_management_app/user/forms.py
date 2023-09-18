from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

# Import custom user model
from django.contrib.auth import get_user_model
custom_user_model = get_user_model()


class CustomUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    username = forms.CharField(label='Username', min_length=4, max_length=150)
    email = forms.EmailField(label='E-Mail')
    first_name = forms.CharField(label='First Name')
    last_name = forms.CharField(label='Last Name')

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = custom_user_model
        fields = ('username', 'first_name', 'last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        return user