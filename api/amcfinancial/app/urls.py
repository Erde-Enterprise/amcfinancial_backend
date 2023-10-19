from django.urls import path

from .views import get_root, login_view, teste_token

urlpatterns = [
    path('', get_root),
    path('login',login_view ),
    path('teste_token', teste_token ),
]