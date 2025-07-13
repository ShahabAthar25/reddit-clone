from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Rule, Subreddit

User = get_user_model()


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ["id", "title", "description", "created_at"]


class SubredditSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Subreddit
        fields = ["id", "name", "description", "owner", "created_at", "icon"]


class SubredditDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    moderators = serializers.SlugRelatedField(
        many=True, slug_field="username", queryset=User.objects.all()
    )
    rules = RuleSerializer(many=True, read_only=True)

    class Meta:
        model = Subreddit
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "moderators",
            "rules",
            "created_at",
            "icon",
            "banner",
        ]
