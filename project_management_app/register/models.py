from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers for authentication instead of usernames.
    """
    def create_user(self, email, first_name, last_name, password=None, **other_fields):
        if not last_name:
            raise ValueError(_('Users must have a last name'))
        elif not first_name:
            raise ValueError(_('Users must have a first name'))
        elif not email:
            raise ValueError(_('Users must provide an email address'))

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **other_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, last_name, password=None, **other_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_admin', True)

        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            password=password,
            **other_fields
        )

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')

        user.save(using=self._db)

        return user

class CustomizedUser(AbstractBaseUser, PermissionsMixin):
    objects = CustomUserManager()

    email = models.EmailField(max_length=200, unique=True)

    is_admin = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_name(self):
        return self.first_name + " " + self.last_name


class WorkingHour(models.Model):
    task = models.ForeignKey('project_task.Task', on_delete=models.CASCADE, blank=True, null=True)
    person = models.ForeignKey('CustomizedUser', on_delete=models.CASCADE)
    date = models.DateField()
    hour = models.DurationField()