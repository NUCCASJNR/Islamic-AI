from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

from users.models import MainUser


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

    def authenticate_header(self, request):
        """

        :param request:

        """
        return 'Bearer realm="api"'


def get_client_ip(request):
    """Retrieves the client's IP address from the request.

    This function attempts to extract the client's IP address from
     the HTTP headers.
    If the 'HTTP_X_FORWARDED_FOR' header is present,
    it contains a comma-separated list of IP addresses, with the client's
     IP address typically being the first one.
    If the 'HTTP_X_FORWARDED_FOR' header is not present,
     the 'REMOTE_ADDR' header is used to obtain the client's IP address.

    :param request: HttpRequest object representing the incoming HTTP request.
    :returns: The client's IP address.
    :rtype: str

    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.META.get("REMOTE_ADDR")
    return client_ip
