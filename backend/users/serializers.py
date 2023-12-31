# django
from django.http import HttpRequest
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from requests.exceptions import HTTPError

# REST
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers, exceptions

# Allauth
from allauth.account import app_settings as allauth_settings
from allauth.utils import (email_address_exists)
from allauth.account.adapter import get_adapter

UserModel = get_user_model()

# User
class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model without password
    """
    class Meta:
        model = UserModel
        fields = ('pk', 'email')
        read_only_fields = ('email', )

# Login
class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        """ Validates the user email for authentication"""
        user = None
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            raise exceptions.ValidationError(_('Must include "email" and "password".'))
        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = self._validate_email(email, password)
        
        # If the user exists
        if user:
            if not user.is_active:
                raise exceptions.ValidationError( _('User account is disabled.'))
        else:
            raise exceptions.ValidationError(_('Unable to log in with provided credentials.'))

        attrs['user'] = user
        return attrs

# Register
class RegisterSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        return user

# JWT 
class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    refresh = serializers.CharField()
    access = serializers.CharField()

# JWT Token Generation
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
    

