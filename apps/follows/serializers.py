from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.serializers import UserSerializer

User = get_user_model()


class FollowerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    profile_picture = serializers.URLField()
