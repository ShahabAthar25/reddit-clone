from django.conf import settings
from django.db import models


class Post(models.Model):
    subreddit = models.ForeignKey(
        "subreddits.Subreddit", related_name="posts", on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    media = models.FileField(upload_to="post_media/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vote_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    is_spoiler = models.BooleanField(default=False)
    is_nsfw = models.BooleanField(default=False)

    # Moderation
    is_removed = models.BooleanField(default=False)
    removal_reason = models.CharField(max_length=255, blank=True, null=True)
    moderator_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subreddit", "owner"]),
            models.Index(fields=["-vote_count"]),
        ]

    def __str__(self):
        return self.title
