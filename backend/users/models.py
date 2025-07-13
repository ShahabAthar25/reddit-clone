from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    bio = models.TextField(max_length=500, blank=True)
    karma_points = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    def is_moderator_of(self, subreddit):
        return self.moderated_subreddits.filter(pk=subreddit.pk).exists()

    def __str__(self):
        return self.username
