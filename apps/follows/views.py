from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.models import Post
from apps.posts.serializers import PostSerializer
from .models import Follow
from .serializers import FollowerSerializer

User = get_user_model()


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.pk == pk:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            Follow.objects.create(follower=request.user, following=target)
        except IntegrityError:
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': f'You are now following {target.username}.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        deleted, _ = Follow.objects.filter(follower=request.user, following_id=pk).delete()
        if not deleted:
            return Response({'detail': 'You are not following this user.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowersListView(generics.ListAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        return User.objects.filter(following__following_id=self.kwargs['pk'])


class FollowingListView(generics.ListAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        return User.objects.filter(followers__follower_id=self.kwargs['pk'])


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        followed_ids = Follow.objects.filter(follower=self.request.user).values_list('following_id', flat=True)
        return (
            Post.objects.filter(author_id__in=followed_ids)
            .select_related('author')
            .order_by('-created_at')
        )
