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

# utils
from .utils import EncodeJWT

# decirators
from .decorators import (
    authentication_sensitive_post_parameters,
    creation_sensitive_post_parameters_m
)

# seralizers
from .seralizers import (
    LoginSerializer, JWTSerializer, RegisterSerializer,
    MyTokenObtainPairSerializer
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
    Return the REST Framework Token Object's key.
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
        self.token = MyTokenObtainPairSerializer.get_token(user)#EncodeJWT(user)
        # complete_signup(self.request._request, user, allauth_settings.EMAIL_VERIFICATION, None)
        return user



















# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.permissions import AllowAny
# from rest_framework.authtoken.models import Token
# from rest_framework.decorators import api_view, permission_classes
# from django.views.decorators.csrf import csrf_exempt
# import json
# from.models import User



# @csrf_exempt
# @api_view(['POST'])
# def login(request):
#     body = json.loads(request.body)
#     email = body.get('email')
#     password = body.get('password')
#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response({'error': 'Invalid username or password'}, status=400)

#     if user.check_password(password):
#         token, created = Token.objects.get_or_create(user=user)
#         response_data = {
#             'token': token.key,
#             'user_id': user.id,
#         }
#         return Response(response_data)
#     return Response({'error': 'Invalid username or password'}, status=400)


# @csrf_exempt
# @api_view(['POST'])
# def register(request):
#     body = json.loads(request.body)
#     email = body.get('email')
#     password = body.get('password')

#     try:
#         user = User.objects.get(email=email)
#         return Response({'error': 'Email already taken'}, status=400)
    
#     # form check for password or somethn
    
#     except User.DoesNotExist:
#         user = User.objects.create_user(email, password, username=email)
#         token, created = Token.objects.get_or_create(user=user)
#         response_data = {
#             'token': token.key,
#             'user_id': user.id,
#         }
#         return Response(response_data)


# @csrf_exempt
# @api_view(['POST'])
# def OauthGoogle(request):
#     body = json.loads(request.body)
#     email = body.get('email')
#     password = body.get('password')

#     if User.objects.filter(email=email).exists():
#         user = User.objects.get(email=email)
#         if user.check_password(password):
#             token, created = Token.objects.get_or_create(user=user)
#             response_data = {
#                 'token': token.key,
#                 'user_id': user.id,
#             }
#             return Response(response_data)
#         else:
#             print(user.check_password(password), password)
#             return Response({'error': 'Invalid username or password'}, status=400)
#     else:
#         user = User.objects.create_user(email, password, username=email)
#         token, created = Token.objects.get_or_create(user=user)
#         response_data = {
#             'token': token.key,
#             'user_id': user.id,
#         }
#         return Response(response_data)
