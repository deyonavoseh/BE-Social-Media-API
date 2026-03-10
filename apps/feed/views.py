from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.posts.models import Post
from apps.posts.serializers import PostSerializer
from apps.users.models import Follow


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['content', 'user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user
        ).values_list('following_id', flat=True)
        return Post.objects.filter(user_id__in=following_ids).select_related('user').prefetch_related('likes', 'comments', 'reposts')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class TrendingPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        seven_days_ago = timezone.now() - timedelta(days=7)
        return Post.objects.filter(
            created_at__gte=seven_days_ago
        ).annotate(like_count=Count('likes')).order_by('-like_count', '-created_at').select_related('user').prefetch_related('likes', 'comments', 'reposts')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context