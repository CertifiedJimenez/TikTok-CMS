# from django.conf.urls import url
from django.urls import path, re_path
from .views import (
    LoginView, LogoutView, RegisterView,
    GoogleLogin
    # SocialAccountDisconnectView, GoogleLoginView
)

from allauth.socialaccount.views import SignupView

urlpatterns = [
    # path(r'^login/$', LoginView.as_view(), name='rest_login'),
    # url(r'^socialaccounts/(?P<pk>\d+)/disconnect/$', SocialAccountDisconnectView.as_view(),
    path('login', LoginView.as_view(), name='rest_login'),
    path('logout', LogoutView.as_view(), name='rest_logout'),
    path('register', RegisterView.as_view(), name='rest_register'),
    path('rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    re_path(r'^accounts/', SignupView.as_view(), name='socialaccount_signup'),

    # path('socialaccounts/<pk>/disconnect/', SocialAccountDisconnectView.as_view(), 
    #      name="socialaccounts_disconnect")
]