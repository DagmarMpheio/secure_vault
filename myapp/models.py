from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# Modelo dos Usuários
class User(AbstractUser):
    email_is_verified = models.BooleanField(default=False)
    login_attempts = models.IntegerField(default=0)
    pass
