# Django
from django.test import TestCase
from django.urls import reverse
from .models import User
import json

# REST
from rest_framework import status
from rest_framework.test import APIClient

class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "cristofer.pro@icloud.com"
        self.password = "_@GitHubGrap555"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.url = reverse("rest_login")

    def test_valid_login(self):
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_invalid_login(self):
        data = {
            "email": self.email,
            "password": "admin",
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)['non_field_errors'][0], 'Unable to log in with provided credentials.')

    def test_missing_email(self):
        data = {
            "email": "",
            "password": "admin",
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(json.loads(response.content)['email'][0], 'This field may not be blank.')

class SignUpTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "cristofer.pro@icloud.com"
        self.password = "_@GitHubGrap555"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.url = reverse("rest_register")
    

    def test_successful_registration(self):
        data = {
            "email": "new_user@example.com",
            "password1": "HASH_CheesBurger21",
            "password2": "HASH_CheesBurger21",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
    
    def test_registration_with_bad_password(self):
        data = {
            "email": "new_user@example.com",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)['password1'][0],'This password is too common.')
    
    def test_registration_with_password_mismatch(self):
        data = {
            "email": "new_user@example.com",
            "password1": "HASH_CheesBurger21",
            "password2": "HASH_CheesBurger12",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)['non_field_errors'][0], "The two password fields didn't match.")

    def test_registration_with_missing_email(self):
        data = {
            "email": "",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)['email'][0], 'This field may not be blank.')


    def test_registration_with_existing_email(self):
        data = {
            "email": "cristofer.pro@icloud.com",  # Using the email set up in the `SignUpTest`
            "password1": "_@GitHubGrap555",
            "password2": "_@GitHubGrap555",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)['email'][0], "A user is already registered with this e-mail address.")
