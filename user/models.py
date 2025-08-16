from django.db import models
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

class FirstLoginRecord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_first_login = models.BooleanField(default=True)
