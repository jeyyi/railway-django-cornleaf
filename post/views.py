from django.shortcuts import render
from rest_framework import viewsets
from .models import Post, Picture
from .serializers import PostSerializer, PictureSerializer
from django_filters.rest_framework import DjangoFilterBackend

class PostAPI(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-id')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'id', 'blight', 'rust', 'gray_leaf_spot', 'other']


class PictureAPI(viewsets.ModelViewSet):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer