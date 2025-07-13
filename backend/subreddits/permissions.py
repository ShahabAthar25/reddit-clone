from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Subreddit


class IsSubredditOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        subreddit_pk = view.kwargs.get("subreddit_pk")
        if not subreddit_pk:
            return False

        try:
            subreddit = Subreddit.objects.get(pk=subreddit_pk)
        except Subreddit.DoesNotExist:
            return False

        return subreddit.owner == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        subreddit_pk = view.kwargs.get("subreddit_pk")

        if not subreddit_pk:
            return False

        subreddit = get_object_or_404(Subreddit, pk=subreddit_pk)

        return subreddit.moderators.filter(pk=request.user.pk).exists()
