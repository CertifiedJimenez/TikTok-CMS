# tests.py
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from .models import post

class PostViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_list(self):
        url = reverse('posts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
    Due to the POSTS app not required and demo 
    I have not continued with the unit tests.
    """

    # def test_create_post(self):
    #     url = reverse('posts')
    #     data = {
    #         'caption': 'Test caption',
    #         'video': 'FIRST_cold_plunge_did_not_go_as_expected_.mp4'
    #     }
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(post.objects.count(), 1)

