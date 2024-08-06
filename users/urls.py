# myapp/urls.py
from django.urls import path
from .api import api  # Import the API object from your api.py file

urlpatterns = [
    path('api/', api.urls),
]
