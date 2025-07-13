from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response
from users.serializers import UserSerializer

from .models import Rule, Subreddit
from .permissions import (IsModeratorOrReadOnly, IsOwnerOrReadOnly,
                          IsSubredditOwner)
from .serializers import (RuleSerializer, SubredditDetailSerializer,
                          SubredditSerializer)

User = get_user_model()


class ModeratorViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsSubredditOwner]
    serializer_class = UserSerializer
    lookup_field = "pk"

    def get_subreddit(self):
        subreddit_pk = self.kwargs["subreddit_pk"]
        return get_object_or_404(Subreddit, pk=subreddit_pk)

    def get_queryset(self):
        try:
            subreddit = Subreddit.objects.get(pk=self.kwargs["subreddit_pk"])
            return subreddit.moderators.all()
        except Subreddit.DoesNotExist:
            return User.objects.none()

    def create(self, request, *args, **kwargs):
        subreddit = self.get_subreddit()
        user_id = request.data.get("id")

        if not user_id:
            return Response(
                {"error": "A user 'id' must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_to_add = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if subreddit.moderators.filter(pk=user_to_add.pk).exists():
            return Response(
                {"error": "User is already a moderator."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subreddit.moderators.add(user_to_add)
        serializer = self.get_serializer(user_to_add)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_destroy(self, instance):
        subreddit = self.get_subreddit()

        if instance == subreddit.owner:
            raise ValidationError(
                "The subreddit owner cannot be removed as a moderator."
            )

        subreddit.moderators.remove(instance)


class SubredditViewSet(viewsets.ModelViewSet):
    queryset = Subreddit.objects.all()

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return SubredditDetailSerializer
        return SubredditSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action == "create":
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        subreddit = serializer.save(owner=self.request.user)
        subreddit.moderators.add(self.request.user)


class RuleViewSet(viewsets.ModelViewSet):
    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsModeratorOrReadOnly]

    def get_queryset(self):
        return Rule.objects.filter(subreddit_id=self.kwargs["subreddit_pk"])

    def perform_create(self, serializer):
        subreddit = Subreddit.objects.get(pk=self.kwargs["subreddit_pk"])
        serializer.save(subreddit=subreddit)
