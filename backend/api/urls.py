from django.urls import include, path

urlpatterns = [
    path("subreddits/", include("subreddits.urls")),
]
