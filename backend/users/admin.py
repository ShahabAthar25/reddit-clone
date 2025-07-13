from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Defines the admin interface for the CustomUser model.
    """

    model = CustomUser

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "karma_points",
        "is_staff",
    )

    # Customize the fields available on the user editing page.
    # This creates a new section called "Custom Profile Info" on the user detail page.
    fieldsets = UserAdmin.fieldsets + (
        (
            "Custom Profile Info",
            {
                "fields": ("profile_picture", "bio", "karma_points", "role"),
            },
        ),
    )

    # Customize the fields on the user creation form ("Add user").
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Custom Fields",
            {
                "fields": ("email", "role", "bio"),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
