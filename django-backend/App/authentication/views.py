from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
import json
from.models import User



@csrf_exempt
@api_view(['POST'])
def login(request):
    body = json.loads(request.body)
    email = body.get('email')
    password = body.get('password')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid username or password'}, status=400)

    if user.check_password(password):
        token, created = Token.objects.get_or_create(user=user)
        response_data = {
            'token': token.key,
            'user_id': user.id,
        }
        return Response(response_data)
    return Response({'error': 'Invalid username or password'}, status=400)


@csrf_exempt
@api_view(['POST'])
def register(request):
    body = json.loads(request.body)
    email = body.get('email')
    password = body.get('password')

    try:
        user = User.objects.get(email=email)
        return Response({'error': 'Email already taken'}, status=400)
    
    # form check for password or somethn
    
    except User.DoesNotExist:
        user = User.objects.create_user(email, password, username=email)
        token, created = Token.objects.get_or_create(user=user)
        response_data = {
            'token': token.key,
            'user_id': user.id,
        }
        return Response(response_data)


@csrf_exempt
@api_view(['POST'])
def OauthGoogle(request):
    body = json.loads(request.body)
    email = body.get('email')
    password = body.get('password')

    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            response_data = {
                'token': token.key,
                'user_id': user.id,
            }
            return Response(response_data)
        else:
            print(user.check_password(password), password)
            return Response({'error': 'Invalid username or password'}, status=400)
    else:
        user = User.objects.create_user(email, password, username=email)
        token, created = Token.objects.get_or_create(user=user)
        response_data = {
            'token': token.key,
            'user_id': user.id,
        }
        return Response(response_data)
