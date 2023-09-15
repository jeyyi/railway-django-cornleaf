from rest_framework import serializers
from .models import Post, Picture
from comments.models import Comment
from comments.serializers import CommentSerializer

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()
    author_type = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)
    is_classification = serializers.BooleanField(required=False)
    is_multiple_classification = serializers.BooleanField(required=False)
    total_blight = serializers.IntegerField(required=False)
    total_rust = serializers.IntegerField(required=False)
    total_gray_leaf_spot = serializers.IntegerField(required=False)
    total_healthy = serializers.IntegerField(required=False)
    total_other = serializers.IntegerField(required=False)


    class Meta:
        model = Post
        fields = "__all__"

    def get_author_name(self, obj):
        return str(obj.author.first_name + ' ' + obj.author.last_name)

    def get_author_type(self, obj: Post):
        return 'farmer' if obj.author.user_type in ['user', 'farmer'] else obj.author.user_type

    def get_tags(self, obj):
        tag_list = []
        tag_dict = {
            'blight': obj.blight,
            'rust': obj.rust,
            'healthy': obj.healthy,
            'gray_leaf_spot': obj.gray_leaf_spot,
            'other': obj.other,
        }
        for name, value in tag_dict.items():
            if value:
                tag_list.append(name)
        
        return tag_list
    
    def get_author_image(self, obj:Post):
        if obj.author.picture:
           return f'https://2023-lamba-bucket.s3.amazonaws.com/media/{obj.author.picture}'
        return None 

    def get_comments(self, obj):
        post_id = obj.id
        comments = Comment.objects.filter(post_id=post_id)
        comment_serializer = CommentSerializer(comments, many=True)
        return comment_serializer.data
class PictureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Picture
        fields = "__all__"