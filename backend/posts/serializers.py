from rest_framework import serializers
from subreddits.models import Subreddit
from subreddits.serializers import SubredditSerializer
from users.serializers import UserSerializer

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    subreddit = SubredditSerializer(read_only=True)
    subreddit_id = serializers.PrimaryKeyRelatedField(
        queryset=Subreddit.objects.all(), source="subreddit", write_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "subreddit",
            "subreddit_id",
            "owner",
            "title",
            "body",
            "url",
            "media",
            "created_at",
            "updated_at",
            "vote_count",
            "comment_count",
            "is_spoiler",
            "is_nsfw",
        ]
        read_only_fields = ["owner", "vote_count", "comment_count"]

    def validate(self, data):
        if not data.get("body") and not data.get("url") and not data.get("media"):
            raise serializers.ValidationError(
                "A post must have a body, a URL, or a media file."
            )
        return data

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
