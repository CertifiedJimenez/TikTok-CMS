# from django.conf.urls import url
from django.urls import path
from .views import (
    LoginView, LogoutView, RegisterView
)


urlpatterns = [
    # path(r'^login/$', LoginView.as_view(), name='rest_login'),
    path('login', LoginView.as_view(), name='rest_login'),
    path('logout', LogoutView.as_view(), name='rest_logout'),
    path('register', RegisterView.as_view(), name='rest_register'),
]