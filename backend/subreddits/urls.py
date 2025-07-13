from rest_framework_nested import routers

from .views import ModeratorViewSet, RuleViewSet, SubredditViewSet

# Main router for /subreddits/
router = routers.DefaultRouter()
router.register(r"subreddits", SubredditViewSet, basename="subreddit")

# Nested router for /subreddits/{subreddit_pk}/rule|moderators
subreddits_router = routers.NestedDefaultRouter(
    router, r"subreddits", lookup="subreddit"
)
subreddits_router.register(r"rules", RuleViewSet, basename="subreddit-rules")
subreddits_router.register(
    r"moderators", ModeratorViewSet, basename="subreddit-moderators"
)

urlpatterns = router.urls + subreddits_router.urls
