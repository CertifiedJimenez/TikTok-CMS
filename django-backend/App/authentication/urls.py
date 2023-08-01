# from django.conf.urls import url
from django.urls import path
from .views import (
    LoginView, LogoutView, RegisterView,
    SocialAccountDisconnectView, GoogleLogin
)

urlpatterns = [
    # path(r'^login/$', LoginView.as_view(), name='rest_login'),
    # url(r'^socialaccounts/(?P<pk>\d+)/disconnect/$', SocialAccountDisconnectView.as_view(),
    path('login', LoginView.as_view(), name='rest_login'),
    path('logout', LogoutView.as_view(), name='rest_logout'),
    path('register', RegisterView.as_view(), name='rest_register'),
    path('rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('socialaccounts/<pk>/disconnect/', SocialAccountDisconnectView.as_view(), 
         name="socialaccounts_disconnect")
]