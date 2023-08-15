from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_type = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"

    def get_author_name(self, obj: Comment):
        return str(obj.author.first_name + ' ' + obj.author.last_name)
    
    def get_author_type(self, obj: Comment):
        return str(obj.author.user_type)
    
    def get_author_image(self, obj: Comment):

        return f'https://2023-lamba-bucket.s3.amazonaws.com/media/{obj.author.picture}'