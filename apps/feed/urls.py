from django.urls import path
from .views import FeedView, TrendingPostsView

urlpatterns = [
    path('', FeedView.as_view(), name='feed'),
    path('trending/', TrendingPostsView.as_view(), name='trending-posts'),
]