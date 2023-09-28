from django.utils.translation import gettext as _
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomizedUser.

    This manager customizes the user creation process to use the email as the
    primary unique identifier instead of the traditional username. It also provides
    utility functions to create regular users and superusers.
    """

    def create_user(self, username, email, first_name, last_name, password=None, **other_fields):
        """
        Create and return a new user with the given email, first name, last name, and password.

        Args:
            - username (str): The desired username for the user. Must be unique.
            - email (str): The email address of the user. Must be unique.
            - first_name (str): The first name of the user.
            - last_name (str): The last name of the user.
            - password (str, optional): The password for the user. Defaults to None.
            - other_fields (dict): Any other fields to be set on the user.

        Returns:
            CustomizedUser: The created user.
        """
        # Validate essential fields
        if not username:
            raise ValueError(_('Users must have a username'))
        if not email:
            raise ValueError(_('Users must provide an email address'))
        if not first_name:
            raise ValueError(_('Users must have a first name'))
        if not last_name:
            raise ValueError(_('Users must have a last name'))

        # Create the user
        user = self.model(
            username=username,
            email=self.normalize_email(email),  # normalize email address by lowercasing the domain part of it
            first_name=first_name,
            last_name=last_name,
            **other_fields
        )
        user.set_password(password)  # set user password
        user.save(using=self._db)  # save the user to the database

        return user

    def create_superuser(self, username, email, first_name, last_name, password=None, **other_fields):
        """
        Create and return a new superuser with the given details.

        Args are similar to create_user with the addition that superusers are
        always set with `is_staff`, `is_superuser`, and `is_admin` as True.
        """
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_admin', True)

        # Validations for superuser
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')

        return self.create_user(username, email, first_name, last_name, password, **other_fields)


class CustomizedUser(AbstractBaseUser, PermissionsMixin):
    """
    Customized User model.

    This model represents a custom user for the application, using email as the primary
    unique identifier for authentication instead of the traditional username.

    Fields:
        - email (EmailField): User's email address.
        - username (CharField): User's username. Unique across the system.
        - first_name (CharField): User's first name.
        - last_name (CharField): User's last name.
        - is_admin (BooleanField): Designates if the user has admin privileges.
        - is_superuser (BooleanField): Designates if the user has superuser privileges.
        - is_staff (BooleanField): Designates if the user can access the admin site.
        - is_active (BooleanField): Designates if the user account is active.
        - scrum_role (ForeignKey): Role of the user in Scrum.
        - date_joined (DateTimeField): Date and time the user joined the system.
    """
    objects = CustomUserManager()

    # Login Details
    username = models.CharField(max_length=30, unique=True, verbose_name=_("Username"))

    # Personal info
    email = models.EmailField(max_length=200, unique=True, verbose_name=_("Email Address"))
    first_name = models.CharField(max_length=200, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=200, verbose_name=_("Last Name"))

    # Permission
    is_superuser = models.BooleanField(default=False, verbose_name=_("Superuser"))
    is_staff = models.BooleanField(default=True, verbose_name=_("Staff"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    # Additional info
    scrum_role = models.ForeignKey('ScrumRole', on_delete=models.CASCADE, blank=True, null=True,
                                   verbose_name=_("Scrum Role"))

    # default required fields
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=_("Date Joined"))
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def get_name(self):
        """
        Returns the full name of the user.

        Returns:
            str: Full name in the format "First Name Last Name".
        """
        return f"{self.first_name} {self.last_name}"


class WorkingHour(models.Model):
    """
    This class is used to create a model for working hours.
    """
    task = models.ForeignKey('project_task.Task', on_delete=models.CASCADE, blank=True, null=True)
    person = models.ForeignKey('CustomizedUser', on_delete=models.CASCADE)
    date = models.DateField()
    hour = models.DurationField()


class ScrumRole(models.Model):
    """
    This class is used to create a model for scrum roles.
    """
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name
