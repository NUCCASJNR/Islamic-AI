#!/usr/bin/env python3

"""Contains user model definition"""

from django.contrib.auth.models import AbstractUser
from utils.base_model import BaseModel, models


class MainUser(AbstractUser, BaseModel):
    """
    Main user model
    """
    first_name: str = models.CharField(max_length=150)
    last_name: str = models.CharField(max_length=150)
    email: str = models.EmailField(unique=True, blank=False, null=False)
    username: str = models.CharField(max_length=55, unique=True, blank=False, null=False)
    password: str = models.CharField(max_length=255, blank=False, null=False)
    is_verified = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=6, null=True, blank=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)