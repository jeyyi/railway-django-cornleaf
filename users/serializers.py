from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from users.models import Profile


class MyUserSerializer(UserSerializer):
    # Add the custom fields here
    user_type = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    picture = serializers.ImageField(required=False)

    class Meta(UserSerializer.Meta):
        fields = tuple(UserSerializer.Meta.fields) + ('user_type', 'first_name', 'last_name', 'picture')

class MyUserCreateSerializer(UserCreateSerializer):
    # Add the custom fields here
    user_type = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    picture = serializers.ImageField(required=False)

    class Meta(UserCreateSerializer.Meta):
        fields = tuple(UserCreateSerializer.Meta.fields) + ('user_type', 'first_name', 'last_name', 'picture', )


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"