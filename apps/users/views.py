from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import User, Follow
from .serializers import (
    UserRegistrationSerializer, UserPublicSerializer,
    UserPrivateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'message': 'User registered successfully.', 'user': UserPrivateSerializer(user).data}, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserPrivateSerializer(request.user).data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserPrivateSerializer(request.user).data)

    def delete(self, request):
        request.user.delete()
        return Response({'message': 'Account deleted.'}, status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed successfully.'})


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['username', 'bio']
    ordering_fields = ['username', 'created_at']
    ordering = ['-created_at']


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        _, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            return Response({'message': f'Already following @{username}.'})
        return Response({'message': f'Now following @{username}.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, username):
        target = get_object_or_404(User, username=username)
        deleted, _ = Follow.objects.filter(follower=request.user, following=target).delete()
        if not deleted:
            return Response({'error': f'You are not following @{username}.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f'Unfollowed @{username}.'})


class FollowersListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return User.objects.filter(following__following=user)


class FollowingListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return User.objects.filter(followers__follower=user)