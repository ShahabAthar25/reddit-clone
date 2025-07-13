from django.core.cache import cache
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post
from .permissions import IsOwnerOrReadOnly
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # Enables filtering like: /api/posts/?subreddit__name=django
    filterset_fields = {
        "subreddit__name": ["exact"],
        "owner__username": ["exact"],
        "created_at": [
            "gte",
            "lte",
            "exact",
            "gt",
            "lt",
        ],
    }

    # Enables search like: /api/posts/?search=API
    search_fields = ["title", "body"]

    # Enables ordering like: /api/posts/?ordering=-vote_count
    ordering_fields = ["created_at", "vote_count", "comment_count"]

    def get_queryset(self):
        return Post.objects.filter(is_removed=False).select_related(
            "owner", "subreddit"
        )

    def perform_create(self, serializer):
        subreddit = serializer.validated_data.get("subreddit")

        if not subreddit.members.filter(id=self.request.user.id).exists():
            raise permissions.PermissionDenied(
                "You must be a member of this subreddit to post."
            )

        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if not (
            instance.owner == self.request.user
            or self.request.user.is_moderator_of(instance.subreddit)
        ):
            self.permission_denied(self.request)

        instance.is_removed = True
        instance.body = "[deleted]"
        instance.save()

    @action(detail=False, methods=["get"])
    def trending(self, request):
        trending_posts_cache_key = "trending_posts"
        cached_posts = cache.get(trending_posts_cache_key)

        if cached_posts:
            serializer = self.get_serializer(cached_posts, many=True)
            return Response(serializer.data)

        # Get top 10 posts from the last 3 days, ordered by votes.
        from django.utils import timezone

        three_days_ago = timezone.now() - timezone.timedelta(days=10)

        trending_posts = (
            self.get_queryset()
            .filter(created_at__gte=three_days_ago)
            .order_by("-vote_count")[:20]
        )

        cache.set(trending_posts_cache_key, trending_posts, timeout=82800)  # One day

        serializer = self.get_serializer(trending_posts, many=True)
        return Response(serializer.data)
