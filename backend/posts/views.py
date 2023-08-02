
# REST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

# Serializers
from .serializers import PostSerializer
from .models import post

# Utils
import logging
logger = logging.getLogger(__name__)


class PostView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, format=None):
        latest_posts = post.objects.all().order_by('-id')[:50]
        serializer = PostSerializer(latest_posts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        request.data['posted_by'] = request.user.id
        print(request.data)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk, format=None):
        try:
            post_to_delete = post.objects.get(pk=pk, posted_by=request.user)
        except post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=400)
        post_to_delete.delete()
        return Response({'detail': 'Post successfully deleted.'}, status=204)

    def put(self, request, pk, format=None):
            try:
                post_to_update = post.objects.get(pk=pk, posted_by=request.user)
            except post.DoesNotExist:
                return Response({'detail': 'You do not have permission to update.'}, status=404)

            serializer = PostSerializer(post_to_update, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

    def patch(self, request, pk, format=None):
        return self.put(request, pk, format=format)