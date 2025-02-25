from django.contrib.auth.models import AbstractUser
from django.db import models
from accounts.managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=11, unique=True)
    otp_code = models.PositiveSmallIntegerField(blank=True, null=True)
    otp_created = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone_number'
    objects = CustomUserManager()
    backend = 'accounts.backends.PhoneAuthenticationBackend'

