from django.conf import settings
from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import post

class PostSerializer(serializers.ModelSerializer):

    video_url = serializers.SerializerMethodField()
    picture_url = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = post
        fields = '__all__'
    
    def get_username(self, obj):
        return obj.posted_by.email

    def get_video_url(self, obj):
        if obj.video:
            return self.build_absolute_url(obj.video.url)
        return None

    def get_picture_url(self, obj):
        if obj.Picture:
            return self.build_absolute_url(obj.Picture.url)
        return None

    def build_absolute_url(self, file_url):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(file_url)
        return None
