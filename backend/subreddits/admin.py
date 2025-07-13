from django.contrib import admin

from .models import Rule, Subreddit


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("title", "subreddit", "created_at")
    list_filter = ("subreddit",)
    search_fields = ("title", "description", "subreddit__name")
    readonly_fields = ("created_at",)


class RuleInline(admin.TabularInline):
    model = Rule
    fields = ("title", "description", "created_at")
    readonly_fields = ("created_at",)
    # Provides one extra blank row for adding a new rule
    extra = 1


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    inlines = [RuleInline]

    # Customize the list view
    list_display = ("name", "owner", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "owner__username", "description")

    readonly_fields = (
        "owner",
        "created_at",
    )

    # Use a more user-friendly widget for the moderators many-to-many field
    filter_horizontal = ("moderators",)

    # Organize the fields into logical groups (fieldsets)
    fieldsets = (
        (None, {"fields": ("name", "owner", "description")}),
        ("Branding", {"fields": ("icon", "banner")}),
        ("Moderation", {"fields": ("moderators",)}),
        ("Metadata", {"fields": ("created_at",)}),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            # This is the 'add' view, show a simplified form
            return (
                (None, {"fields": ("name", "description")}),
                ("Branding", {"fields": ("icon", "banner")}),
                ("Moderation", {"fields": ("moderators",)}),
            )
        return super().get_fieldsets(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user

        super().save_model(request, obj, form, change)

        if not change:
            obj.moderators.add(request.user)
