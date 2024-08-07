from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

from .models import MainUser


class CustomBackend(ModelBackend):
    """ """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """

        :param request:
        :param username:  (Default value = None)
        :param password:  (Default value = None)
        :param **kwargs:

        """
        if username is None:
            return None
        if "@" in username:
            kwargs = {"email": username}
        else:
            kwargs = {"username": username}
        try:
            user = MainUser.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None
