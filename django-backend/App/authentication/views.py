# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import (
    login as django_login,
    logout as django_logout
)

# REST
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotFound

# allAuth
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.adapter import get_adapter as get_social_adapter
from allauth.account.adapter import get_adapter
from allauth.socialaccount import signals
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client


# utils
from .utils import EncodeJWT

# seralizers
from .seralizers import (
    LoginSerializer, JWTSerializer, RegisterSerializer,
    MyTokenObtainPairSerializer, SocialLoginSerializer, 
    SocialConnectSerializer, #GoogleLoginSerializer
)

# decorators
from .decorators import (
    authentication_sensitive_post_parameters,
    creation_sensitive_post_parameters_m
)

# def register_permission_classes():
#     permission_classes = [AllowAny, ]
#     for klass in getattr(settings, 'REST_AUTH_REGISTER_PERMISSION_CLASSES', tuple()):
#         permission_classes.append(import_callable(klass))
#     return tuple(permission_classes)


class LoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.

    Accept the following POST parameters: username, password
    Return the REST Framework JWT Object's key.
    """

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @authentication_sensitive_post_parameters
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        return django_login(self.request, self.user)

    def login(self):
        """ authenticates the user and processes the login and generates the token"""
        self.user = self.serializer.validated_data['user']
        self.token = MyTokenObtainPairSerializer.get_token(self.user) #EncodeJWT(self.user)
        return self.process_login()

    def get_response_serializer(self):
        """ Uses the seralizer method to return """
        response_serializer = JWTSerializer
        return response_serializer
    
    def get_response(self):
        """ Returns the data and prarses the object """
        serializer_class = self.get_response_serializer()
        data = {
            'refresh': str(self.token),
            'access': str(self.token.access_token),
        }
        serializer = serializer_class(instance=data, context={'request': self.request})
        response = Response(serializer.data, status=status.HTTP_200_OK)

        """ Assigns the expiry date for the cookie """
        if getattr(settings, 'SIMPLE_JWT', False):
            from App.settings import SIMPLE_JWT
            from datetime import datetime
            expiration = (datetime.utcnow() + SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
            response.set_cookie(SIMPLE_JWT['JWT_AUTH_COOKIE'], self.token, expires=expiration, httponly=True)
        return response

    def post(self, request, *args, **kwargs):
        """ Handles the POST request of the user """
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data, context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        
        self.login()
        return self.get_response()

class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        django_logout(request)
        response = Response({"detail": _("Successfully logged out.")}, status=status.HTTP_200_OK)
        if getattr(settings, 'SIMPLE_JWT', False):
            from App.settings import SIMPLE_JWT
            response.delete_cookie(SIMPLE_JWT['JWT_AUTH_COOKIE'])
        return response

class RegisterView(CreateAPIView):
    """
    Creates a user account and returns the REST Token
    if the input is valid it will create an account.

    Accept the following POST parameters: username, password1, password2
    Return the REST Framework JWT Object's key.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny, ]

    @creation_sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):
        # if allauth_settings.EMAIL_VERIFICATION == allauth_settings.EmailVerificationMethod.MANDATORY:
        #     return {"detail": _("Verification e-mail sent.")}
        data = {
            'refresh': str(self.token),
            'access': str(self.token.access_token),
        }
        return JWTSerializer(data).data
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_response_data(user), status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        self.token = MyTokenObtainPairSerializer.get_token(user) #EncodeJWT(user)
        # complete_signup(self.request._request, user, allauth_settings.EMAIL_VERIFICATION, None)
        return user

class SocialLoginView(LoginView):
    """
    class used for social authentications
    """
    serializer_class = SocialLoginSerializer

    def process_login(self):
        print(get_social_adapter(self.request))
        get_adapter(self.request).login(self.request, self.user)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)






from django.conf import settings

import jwt

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from allauth.socialaccount.providers.google.provider import GoogleProvider


ACCESS_TOKEN_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ACCESS_TOKEN_URL", "https://oauth2.googleapis.com/token")
)

AUTHORIZE_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ACCESS_TOKEN_URL", "https://accounts.google.com/o/oauth2/v2/auth")
)

ID_TOKEN_ISSUER = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ID_TOKEN_ISSUER", "https://accounts.google.com")
)

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


class CustomGoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    id_token_issuer = ID_TOKEN_ISSUER

    def complete_login(self, request, app, token, response, **kwargs):
        try:
            identity_data = jwt.decode(
                response,
                # Since the token was received by direct communication
                # protected by TLS between this library and Google, we
                # are allowed to skip checking the token signature
                # according to the OpenID Connect Core 1.0
                # specification.
                # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
                options={
                    "verify_signature": False,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                },
                issuer=self.id_token_issuer,
                audience=app.client_id,
                verify = False
            )
        except jwt.PyJWTError as e:
            raise OAuth2Error("Invalid id_token") from e
        login = self.get_provider().sociallogin_from_response(request, identity_data)
        return login



class GoogleLogin(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter




# ======================================
# # class SocialLoginView(LoginView):
# #     """
# #     class used for social authentications
# #     """
# #     serializer_class = SocialLoginSerializer

# #     def process_login(self):
# #         get_adapter(self.request).login(self.request, self.user)

# # class GoogleLoginView(SocialLoginView):
# #     serializer_class = GoogleLoginSerializer
# #     adapter_class = GoogleOAuth2Adapter
# #     # client_class = OAuth2Client
# #     # callback_url = '/'

# #     def get_serializer(self, *args, **kwargs):
# #         serializer_class = self.get_serializer_class()
# #         kwargs['context'] = self.get_serializer_context()
# #         return serializer_class(*args, **kwargs)

# class SocialAccountDisconnectView(GenericAPIView):
#     """
#     Disconnect SocialAccount from remote service for
#     the currently logged in user
#     """
#     serializer_class = SocialConnectSerializer
#     permission_classes = (IsAuthenticated,)

#     def get_queryset(self):
#         return SocialAccount.objects.filter(user=self.request.user)

#     def post(self, request, *args, **kwargs):
#         accounts = self.get_queryset()
#         account = accounts.filter(pk=kwargs['pk']).first()
#         if not account:
#             raise NotFound

#         get_social_adapter(self.request).validate_disconnect(account, accounts)

#         account.delete()
#         signals.social_account_removed.send(
#             sender=SocialAccount,
#             request=self.request,
#             socialaccount=account
#         )

#         return Response(self.get_serializer(account).data)


# =========================================
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from rest_auth.registration.views import SocialLoginView

# class GoogleLogin(SocialLoginView):
# # Custom adapter is created because obsolete URLs are used inside django-allauth library
#     class GoogleAdapter(GoogleOAuth2Adapter):
#         access_token_url = "https://oauth2.googleapis.com/token"
#         authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
#         profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"

#     adapter_class = GoogleAdapter
#     callback_url = "http://replace-with-your-url.com/oauth/"
#     client_class = OAuth2Client

#     def get(self, request, *args, **kwargs):
#         print("YESSSSSSSSSSSSSSS")