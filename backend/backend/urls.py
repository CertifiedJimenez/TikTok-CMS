"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.conf import settings

# REST
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Users
from users.views import (
    LoginView, LogoutView, RegisterView,
    GoogleLogin
)

# allAuth
from allauth.socialaccount.views import SignupView

urlpatterns = [

    path('posts/', include('posts.urls')),
    path('admin/', admin.site.urls),
    path('api/login', LoginView.as_view(), name='rest_login'),
    path('api/logout', LogoutView.as_view(), name='rest_logout'),
    path('api/register', RegisterView.as_view(), name='rest_register'),
    path('api/token/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/rest-auth/google_login/', GoogleLogin.as_view(), name='google_login'),
    path('api/rest-auth/socialaccount_signup', SignupView.as_view(), name='socialaccount_signup'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
