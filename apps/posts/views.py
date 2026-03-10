from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Like, Comment
from .serializers import PostSerializer, PostCreateSerializer, LikeSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['content', 'user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.select_related('user').prefetch_related('likes', 'comments', 'reposts').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        full = PostSerializer(serializer.instance, context={'request': request})
        return Response(full.data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Post.objects.select_related('user').prefetch_related('likes', 'comments', 'reposts').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PostCreateSerializer
        return PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.filter(user__username=self.kwargs['username']).select_related('user').prefetch_related('likes', 'comments', 'reposts')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        _, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({'message': 'Already liked.', 'likes_count': post.likes_count})
        return Response({'message': 'Post liked.', 'likes_count': post.likes_count}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if not deleted:
            return Response({'error': 'You have not liked this post.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Post unliked.', 'likes_count': post.likes_count})


class PostLikesListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return Like.objects.filter(post=post).select_related('user')


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['pk']).select_related('user')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_pk'], post_id=self.kwargs['post_pk'])


class RepostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        original = get_object_or_404(Post, pk=pk)
        if original.user == request.user:
            return Response({'error': 'You cannot repost your own post.'}, status=status.HTTP_400_BAD_REQUEST)
        if Post.objects.filter(user=request.user, original_post=original, is_repost=True).exists():
            return Response({'error': 'Already reposted.'}, status=status.HTTP_400_BAD_REQUEST)
        repost = Post.objects.create(user=request.user, content=original.content, original_post=original, is_repost=True)
        return Response(PostSerializer(repost, context={'request': request}).data, status=status.HTTP_201_CREATED)