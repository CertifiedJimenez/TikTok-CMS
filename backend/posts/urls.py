# Django
from django.urls import path

# views
from .views import PostView

urlpatterns = [
    path('', PostView.as_view(), name='posts'),
]