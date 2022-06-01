from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

# Create your models here.
from django.utils.translation import gettext_lazy


class PathaoUserManager(BaseUserManager):
    """ A custom Manager to deal with emails as unique identifer """

    def _create_user(self, email, password, **extra_fields):
        """ Creates and saves a user with a given email and password"""

        if not email:
            raise ValueError("The Email must be set!")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    is_staff = models.BooleanField(
        gettext_lazy('staff status'),
        default=False,
        help_text=gettext_lazy('Designates whether the user can log in this site')
    )

    is_active = models.BooleanField(
        gettext_lazy('active'),
        default=True,
        help_text=gettext_lazy(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts')
    )

    USERNAME_FIELD = 'email'
    objects = PathaoUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email


class CustomerShop(models.Model):
    primary_phone_number = models.CharField(max_length=20)
    shop_address = models.TextField(max_length=200)
    House = models.TextField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_user')
    full_name = models.CharField(max_length=264, blank=True, null=True)
    secondary_phone_number = models.CharField(max_length=20)
    shop = models.ForeignKey(CustomerShop, on_delete=models.CASCADE, related_name='customer_shop')

    def is_fully_filled(self):
        fields_names = [f.name for f in self._meta.get_fields()]
        for field_name in fields_names:
            value = getattr(self, field_name)
            if value is None or value == '':
                return False
        return True
