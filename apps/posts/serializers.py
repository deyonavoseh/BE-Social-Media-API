from rest_framework import serializers
from .models import Post, Like, Comment
from apps.users.serializers import UserPublicSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class PostMinimalSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'user', 'content', 'media_url', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    reposts_count = serializers.IntegerField(read_only=True)
    is_liked_by_me = serializers.SerializerMethodField()
    recent_comments = serializers.SerializerMethodField()
    original_post = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'content', 'media_url', 'likes_count', 'comments_count', 'reposts_count', 'is_liked_by_me', 'recent_comments', 'is_repost', 'original_post', 'created_at', 'updated_at')

    def get_is_liked_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

    def get_recent_comments(self, obj):
        comments = obj.comments.order_by('-created_at')[:3]
        return CommentSerializer(comments, many=True).data

    def get_original_post(self, obj):
        if obj.is_repost and obj.original_post:
            return PostMinimalSerializer(obj.original_post).data
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'content', 'media_url', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('Post content cannot be empty.')
        return value


class LikeSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'post', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')