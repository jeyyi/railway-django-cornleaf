from rest_framework import serializers
from .models import Post, Picture


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = "__all__"

    def get_author_name(self, obj):
        return str(obj.author.first_name + ' ' + obj.author.last_name)

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

class PictureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Picture
        fields = "__all__"