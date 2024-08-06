#!/usr/bin/env python3

"""Contains user model definition"""

from typing import Union

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group, Permission

from utils.base_model import BaseModel, models


def hash_password(password: Union[str, int]) -> str:
    """Hashes the password

    :param password: str | int
    :param password: Union[str:
    :param in: returns: The hashed password
    :param password: Union[str: 
    :param int]: 
    :returns: The hashed password

    """
    return make_password(password)


class MainUser(AbstractUser, BaseModel):
    """Main user model"""

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, blank=False, null=False)
    username = models.CharField(max_length=55, unique=True, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    is_verified = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=6, null=True, blank=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name="mainuser_set", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="mainuser_set", blank=True
    )

    class Meta:
        """ """

        indexes = [models.Index(fields=["email", "username"])]
        db_table = "users"

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    # Override the custom_save method
    @classmethod
    def custom_save(cls, **kwargs):
        """Overrides the custom_save method to hash the password before saving

        :param **kwargs: 

        """
        if "password" in kwargs:
            kwargs["password"] = hash_password(kwargs["password"])
        return super().custom_save(**kwargs)

    def __str__(self):
        return self.email

    @property
    def full_name(self) -> str:
        """ """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return f"{self.username}"

    @full_name.setter
    def full_name(self, first_name: str, last_name: str) -> None:
        """

        :param first_name: str:
        :param last_name: str:
        :param first_name: str: 
        :param last_name: str: 

        """
        self.first_name = first_name
        self.last_name = last_name
        self.save()
