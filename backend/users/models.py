from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
    )

    # We make email required and unique
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    bio = models.TextField(max_length=500, blank=True)
    karma_points = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    # No need to add username, password, etc. as they are inherited from AbstractUser.

    def __str__(self):
        return self.username
