from rest_framework_nested import routers

from .views import RuleViewSet, SubredditViewSet

# Main router for /subreddits/
router = routers.DefaultRouter()
router.register(r"", SubredditViewSet, basename="subreddit")

# Nested router for /subreddits/{subreddit_pk}/rules/
subreddits_router = routers.NestedDefaultRouter(router, r"", lookup="subreddit")
subreddits_router.register(r"rules", RuleViewSet, basename="subreddit-rules")

urlpatterns = router.urls + subreddits_router.urls
