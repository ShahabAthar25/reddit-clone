from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

# Validator for subreddit names (alphanumeric + underscores only)
validate_subreddit_name = RegexValidator(
    r"^[a-zA-Z0-9_]+$",
    "Subreddit names can only contain letters, numbers, and underscores.",
)


class Subreddit(models.Model):
    name = models.CharField(
        max_length=21, unique=True, validators=[validate_subreddit_name]
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_subreddits",
    )
    moderators = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="moderated_subreddits", blank=True
    )
    icon = models.ImageField(upload_to="subreddit_icons/", null=True, blank=True)
    banner = models.ImageField(upload_to="subreddit_banners/", null=True, blank=True)

    def __str__(self):
        return self.name


class Rule(models.Model):
    subreddit = models.ForeignKey(
        Subreddit, on_delete=models.CASCADE, related_name="rules"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subreddit.name} - Rule: {self.title}"
