from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "id", "email", "first_name", "last_name")

    fieldsets = (
        (
            "Информация о пользователе",
            {
                "fields": (
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                )
            },
        ),
        (
            "Информация об активности",
            {"fields": ("last_login", "date_joined")},
        ),
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
