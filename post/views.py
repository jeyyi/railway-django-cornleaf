from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Post, Picture
from .serializers import PostSerializer, PictureSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView


class PostAPI(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-id')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'id', 'blight', 'rust', 'gray_leaf_spot', 'other', 'is_classification']


class PictureAPI(viewsets.ModelViewSet):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class ListOrBulkDeleteAlbums(APIView):
   

    def delete(self, request, *args, **kwargs):
        # ids = request.query_params.get('ids').split(',')
        # if ids:
        # queryset = Post.objects.filter(id__in=ids)
        queryset = Post.objects.all()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)