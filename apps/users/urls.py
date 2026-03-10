from django.urls import path
from .views import (
    RegisterView, MeView, ChangePasswordView,
    UserListView, UserDetailView,
    FollowView, FollowersListView, FollowingListView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('me/', MeView.as_view(), name='user-me'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', UserListView.as_view(), name='user-list'),
    path('<str:username>/', UserDetailView.as_view(), name='user-detail'),
    path('<str:username>/follow/', FollowView.as_view(), name='user-follow'),
    path('<str:username>/followers/', FollowersListView.as_view(), name='user-followers'),
    path('<str:username>/following/', FollowingListView.as_view(), name='user-following'),
]