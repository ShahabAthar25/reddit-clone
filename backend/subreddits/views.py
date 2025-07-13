from rest_framework import permissions, viewsets

from .models import Rule, Subreddit
from .permissions import IsModeratorOrReadOnly, IsOwnerOrReadOnly
from .serializers import (RuleSerializer, SubredditDetailSerializer,
                          SubredditSerializer)


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
