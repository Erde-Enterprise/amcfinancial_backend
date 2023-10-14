from django.urls import path

from .views import get_root

urlpatterns = [
    path('', get_root),
]