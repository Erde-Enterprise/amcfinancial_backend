from django.urls import path

from .views import get_root, login_view

urlpatterns = [
    path('', get_root),
    path('login',login_view ),
]