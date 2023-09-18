# Custom User Account Model

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager


class CustomAccountManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers for authentication instead of usernames.
    """
    def create_user(self, email, username, first_name, last_name, password=None, **other_fields):
        if not last_name:
            raise ValueError(_('Users must have a last name'))
        elif not first_name:
            raise ValueError(_('Users must have a first name'))
        elif not username:
            raise ValueError(_('Users must have a username'))
        elif not email:
            raise ValueError(_('Users must provide an email address'))

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **other_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **kwargs):
        """
        Create and save a SuperUser with the given email and password.
        """

        # kwargs.setdefault('is_staff', True)
        # kwargs.setdefault('is_superuser', True)
        # kwargs.setdefault('is_admin', True)

        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **kwargs
        )

        # if kwargs.get('is_staff') is not True:
        #     raise ValueError('Superuser must be assigned to is_staff=True.')
        # if kwargs.get('is_superuser') is not True:
        #     raise ValueError('Superuser must be assigned to is_superuser=True.')
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class CustomizedUser(AbstractUser, PermissionsMixin):
    # basic information
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Registration Date
    date_joined = models.DateTimeField(default=timezone.now)  ## todo: unterschied zu 'auto_now_add=True'

    # Permissions
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']  # Note: USERNAME_FIELD not to be included in this list!

    def __str__(self):
        return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin