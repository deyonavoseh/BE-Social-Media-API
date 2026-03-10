from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, UserPostsView,
    LikeToggleView, PostLikesListView,
    CommentListCreateView, CommentDetailView, RepostView,
)

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('user/<str:username>/', UserPostsView.as_view(), name='user-posts'),
    path('<int:pk>/like/', LikeToggleView.as_view(), name='post-like'),
    path('<int:pk>/likes/', PostLikesListView.as_view(), name='post-likes-list'),
    path('<int:pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('<int:post_pk>/comments/<int:comment_pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('<int:pk>/repost/', RepostView.as_view(), name='post-repost'),
]