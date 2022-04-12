from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterFormView.as_view(), name='register'),
    path('perfil/<int:pk>/update', PerfilUpdateView.as_view(), name='perfil'),
]