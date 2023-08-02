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

# auth
try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
    from allauth.socialaccount.models import SocialToken
    from allauth.socialaccount.providers.oauth.client import OAuthError

except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

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

        # If required, is the email verified?
        # if 'rest_auth.registration' in settings.INSTALLED_APPS:
        #     from allauth.account import app_settings
        #     if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
        #         email_address = user.emailaddress_set.get(email=user.email)
        #         if not email_address.verified:
        #             raise serializers.ValidationError(_('E-mail is not verified.'))
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
        # self.custom_signup(request, user)
        # setup_user_email(request, user, [])
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



 
    
# Social media connect Mixin
class SocialConnectMixin(object):
    def get_social_login(self, *args, **kwargs):
        """
        Set the social login process state to connect rather than login
        Refer to the implementation of get_social_login in base class and to the
        allauth.socialaccount.helpers module complete_social_login function.
        """
        social_login = super(SocialConnectMixin, self).get_social_login(*args, **kwargs)
        social_login.state['process'] = AuthProcess.CONNECT
        return social_login

# Social Login
class SocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)

    def _get_request(self):
        request = self.context.get('request')
        if not isinstance(request, HttpRequest):
            request = request._request
        return request

    def get_social_login(self, adapter, app, token, response):
        """
        :param adapter: allauth.socialaccount Adapter subclass.
            Usually OAuthAdapter or Auth2Adapter
        :param app: `allauth.socialaccount.SocialApp` instance
        :param token: `allauth.socialaccount.SocialToken` instance
        :param response: Provider's response for OAuth1. Not used in the
        :returns: A populated instance of the
            `allauth.socialaccount.SocialLoginView` instance
        """
        request = self._get_request()
        social_login = adapter.complete_login(request, app, token, response=response)
        social_login.token = token
        return social_login

    def validate(self, attrs):
        view = self.context.get('view')
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().get_app(request)

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        # Case 1: We received the access_token
        if attrs.get('access_token'):
            access_token = attrs.get('access_token')

        # Case 2: We received the authorization code
        elif attrs.get('code'):
            self.callback_url = getattr(view, 'callback_url', None)
            self.client_class = getattr(view, 'client_class', None)

            if not self.callback_url:
                raise serializers.ValidationError(
                    _("Define callback_url in view")
                )
            if not self.client_class:
                raise serializers.ValidationError(
                    _("Define client_class in view")
                )

            code = attrs.get('code')

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope
            )
            token = client.get_access_token(code)
            access_token = token['access_token']

        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required."))

        social_token = adapter.parse_token({'access_token': access_token})
        social_token.app = app

        try:
            login = self.get_social_login(adapter, app, social_token, access_token)
            complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_("Incorrect value"))

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = get_user_model().objects.filter(
                    email=login.user.email,
                ).exists()
                if account_exists:
                    raise serializers.ValidationError(
                        _("User is already registered with this e-mail address.")
                    )

            login.lookup()
            login.save(request, connect=True)
        attrs['user'] = login.account.user
        return attrs

# Create social
class SocialConnectSerializer(SocialConnectMixin, SocialLoginSerializer):
    pass

# Google Login
class GoogleLoginSerializer(serializers.Serializer):
    pass



    # access_token = serializers.CharField()

    # def _get_request(self):
    #     request = self.context.get('request')
    #     if not isinstance(request, HttpRequest):
    #         request = request._request
    #     return request
    
    # def _account_already_exists(self, email):
    #     try:
    #         user = UserModel.objects.get(email=email)
    #     except UserModel.DoesNotExist:
    #         raise serializers.ValidationError(
    #             _("no user registered with this e-mail address.")
    #         )


    # def _get_social_login(self, token) -> dict:
    #     """
    #     :param adapter: allauth.socialaccount Adapter subclass.
    #         Usually OAuthAdapter or Auth2Adapter
    #     :param app: `allauth.socialaccount.SocialApp` instance
    #     :param token: `allauth.socialaccount.SocialToken` instance
    #     :param response: Provider's response for OAuth1. Not used in the
    #     :returns: A populated instance of the
    #         `allauth.socialaccount.SocialLoginView` instance
    #     """
    #     # request = self._get_request()
    #     # social_login = adapter.complete_login(request, app, token,response=response)
    #     # social_login.token = token


    #     return {}

    # def validate(self, attrs):        
    #     view = self.context.get('view')
    #     request = self._get_request()

    #     if not view:
    #         raise serializers.ValidationError(
    #             _("View is not defined, pass it as a context variable")
    #         )
        
    #     auth_config = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
    #     if not auth_config:
    #         raise serializers.ValidationError(
    #             "SOCIALACCOUNT_PROVIDERS not authenticated for google."
    #         )
        
    #     from .services import google_auth_verification

    #     access_token = attrs.get('access_token')
    #     client_id = auth_config['google']['APP']['client_id']        
    #     token = google_auth_verification(access_token, client_id)
    #     if not token.is_valid:
    #         raise serializers.ValidationError(
    #             _(token.message)
    #         )

    #     user, _ = UserModel.objects.get_or_create(
    #         email=token.info['email'], 
    #         defaults={'email': token.info['email'], 'social_provider': 'GOOGLE'}
    #     )

    #     user.set_password(access_token)      

    #     adapter = get_adapter()
        # user = adapter.new_user(request)
        # self.cleaned_data = self.get_cleaned_data()
        # adapter.save_user(request, user, self)
        # # self.custom_signup(request, user)
        # # setup_user_email(request, user, [])
        # return user

        # user = self._validate_email(token.email, access_token)


        # request.session['oauth_api.twitter.com_access_token'] = {
        #     'oauth_token': access_token,
        #     'oauth_token_secret': token_secret,
        # }
        # print(access_token, token_secret)

        # token = SocialToken(token=access_token, token_secret=token_secret)
        # token.app = app

        # try:
        #     login = self.get_social_login(adapter, app, token, access_token)
        #     print("wwwwwwwwwwwww",login)
        #     complete_social_login(request, login)
        # except OAuthError as e:
        #     raise serializers.ValidationError(str(e))
        # print("032070j209j20j0")

        # if not login.is_existing:
        #     login.lookup()
        #     login.save(request, connect=True)


        # attrs['user'] = user

        # return attrs

# Create social
class GoogleConnectSerializer(SocialConnectMixin, GoogleLoginSerializer):
    pass