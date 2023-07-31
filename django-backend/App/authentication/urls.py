from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='login'),
    path('OauthGoogle', views.OauthGoogle, name="OauthGoogle")
]